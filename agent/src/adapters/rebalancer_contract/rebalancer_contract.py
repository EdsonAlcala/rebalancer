import asyncio
import base64

from typing import Any, Dict

from near_omni_client.transactions import TransactionBuilder, ActionFactory
from near_omni_client.transactions.utils import decode_key
from near_omni_client.json_rpc.exceptions import JsonRpcError

from .views import RebalancerContractViews
from .allowances import RebalancerApprovals
from .state_machine_actions import RebalancerStepMachineActions

class RebalancerContract(RebalancerContractViews, RebalancerApprovals,RebalancerStepMachineActions):
   async def _sign_and_submit_transaction(self, *, method: str, args: Dict[str, Any], gas: int, deposit: int, max_retries: int = 3, delay: float = 2.0):
      public_key_str = await self.near_wallet.get_public_key()
      signer_account_id = self.near_wallet.get_address()
      private_key_str = self.near_wallet.keypair.to_string()
      nonce_and_block_hash = await self.near_client.get_nonce_and_block_hash(signer_account_id, public_key_str)
      
      tx = (
            TransactionBuilder()
            .with_signer_id(signer_account_id)
            .with_public_key(public_key_str)
            .with_nonce(nonce_and_block_hash["nonce"])
            .with_receiver(self.near_contract_id)
            .with_block_hash(nonce_and_block_hash["block_hash"])
            .add_action(
               ActionFactory.function_call(
                  method_name=method,
                  args=args,
                  gas=gas,
                  deposit=deposit,
               )
            )
            .build()
      )

      private_key_bytes = decode_key(private_key_str)
      signed_tx = tx.to_vec(private_key_bytes)
      signed_tx_bytes = bytes(bytearray(signed_tx))
      signed_tx_base64 = base64.b64encode(signed_tx_bytes).decode("utf-8")
      
      # --- Retry section starts here ---
      for attempt in range(1, max_retries + 1):
            try:
               print(f"Sending transaction to NEAR network... (attempt {attempt})")
               result = await self.near_client.send_raw_transaction(signed_tx_base64)
               print("✅ Transaction successfully sent.")
               return result
            except JsonRpcError as e:
               if "TIMEOUT_ERROR" in str(e):
                  if attempt < max_retries:
                        print(f"⚠️  Timeout error on attempt {attempt}. Retrying in {delay:.1f}s...")
                        await asyncio.sleep(delay)
                        delay *= 2  # exponential backoff
                        continue
                  else:
                        print("❌ Transaction failed after maximum retries due to TIMEOUT_ERROR.")
               raise
            except Exception as e:
               # Catch unexpected errors (network, aiohttp, etc.)
               if attempt < max_retries:
                  print(f"⚠️  Unexpected error on attempt {attempt}: {e}. Retrying in {delay:.1f}s...")
                  await asyncio.sleep(delay)
                  delay *= 2
                  continue
               else:
                  print("❌ Transaction failed after maximum retries due to unexpected error.")
                  raise
      # --- Retry section ends here ---
      
