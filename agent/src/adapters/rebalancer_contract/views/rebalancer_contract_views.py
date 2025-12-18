from utils import parse_chain_configs, parse_u32_result, parse_supported_chains
from ..common import _RebalancerBase

class RebalancerContractViews(_RebalancerBase):
    async def get_all_configs(self):
        chain_config_raw = await self.near_client.call_contract(
            contract_id=self.near_contract_id,
            method="get_all_configs",
            args={}
        )
        return parse_chain_configs(chain_config_raw)

    async def get_source_chain(self):
        source_chain_raw = await self.near_client.call_contract(
            contract_id=self.near_contract_id,
            method="get_source_chain",
            args={}
        )
        return parse_u32_result(source_chain_raw)

    async def get_supported_chains(self) -> list[int]:
        supported_chains_raw = await self.near_client.call_contract(
            contract_id=self.near_contract_id,
            method="get_supported_chains",
            args={}
        )
        return parse_supported_chains(supported_chains_raw)