from enum import Enum


class TxType(Enum):
    AaveSupply                        = "AaveSupply"
    AaveWithdraw                      = "AaveWithdraw"
    CCTPBurn                          = "CCTPBurn"
    CCTPMint                          = "CCTPMint"
    RebalancerWithdrawToAllocate      = "RebalancerWithdrawToAllocate"
    RebalancerUpdateCrossChainBalance = "RebalancerUpdateCrossChainBalance"
    RebalancerDeposit                 = "RebalancerDeposit"
    RebalancerSignCrossChainBalance   = "RebalancerSignCrossChainBalance"