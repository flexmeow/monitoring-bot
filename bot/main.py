import asyncio
import os

from tinybot import DEV_GROUP_CHAT_ID, TinyBot, multicall, notify_group_chat

from bot.alerts.forward import post_event
from bot.alerts.poller import telegram_command_loop
from bot.alerts.store import Store
from bot.config import (
    ALERTS_STATE_PATH,
    ALLOCATOR_VAULT_ABI,
    AUCTION_ABI,
    BACKUP_INTERVAL,
    COMMON_REPORT_TRIGGER,
    ERC20_ABI,
    FACTORY_ABI,
    GITHUB_BACKUP_BRANCH,
    GITHUB_BACKUP_PATH,
    GITHUB_REPO,
    GITHUB_TOKEN,
    INTERVAL,
    KEEPER_ABI,
    LENDER_ABI,
    MAX_GAS_GWEI,
    PERMISSIONED_KEEPER,
    PERMISSIONED_KEEPER_ABI,
    PERMISSIONLESS_KEEPER,
    REGISTRY_ABI,
    REPORT_INTERVAL,
    REPORT_TRIGGER_ABI,
    TROVE_MANAGER_ABI,
    allocator_vaults,
    explorer_tx_url,
    factory_addr,
    fmt,
    get_all_auctions,
    get_all_lenders,
    get_all_markets,
    network,
    registry_addr,
    safe_name,
    short,
)

# =============================================================================
# Trove Manager Event Handlers
# =============================================================================


async def on_open_trove(bot: TinyBot, log: object) -> None:
    trove_id: int = log.args.trove_id
    owner: str = log.args.trove_owner
    collateral: int = log.args.collateral_amount
    debt: int = log.args.debt_amount
    upfront_fee: int = log.args.upfront_fee
    rate: int = log.args.annual_interest_rate

    tm = bot.w3.eth.contract(address=log.address, abi=TROVE_MANAGER_ABI)
    coll_token = bot.w3.eth.contract(address=tm.functions.collateral_token().call(), abi=ERC20_ABI)
    borr_token = bot.w3.eth.contract(address=tm.functions.borrow_token().call(), abi=ERC20_ABI)
    coll_sym, coll_dec, borr_sym, borr_dec = multicall(
        bot.w3,
        [
            coll_token.functions.symbol(),
            coll_token.functions.decimals(),
            borr_token.functions.symbol(),
            borr_token.functions.decimals(),
        ],
    )

    await post_event(
        bot,
        f"🏦 <b>Trove Opened</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Collateral:</b> {fmt(collateral / (10**coll_dec))} {coll_sym}\n"
        f"<b>Debt:</b> {fmt(debt / (10**borr_dec))} {borr_sym}\n"
        f"<b>Upfront Fee:</b> {fmt(upfront_fee / (10**borr_dec))} {borr_sym}\n"
        f"<b>Interest Rate:</b> {rate / (10 ** (borr_dec - 2)):.2f}%\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>",
        owner,
    )


async def on_close_trove(bot: TinyBot, log: object) -> None:
    trove_id: int = log.args.trove_id
    owner: str = log.args.trove_owner
    collateral: int = log.args.collateral_amount
    debt: int = log.args.debt_amount

    tm = bot.w3.eth.contract(address=log.address, abi=TROVE_MANAGER_ABI)
    coll_token = bot.w3.eth.contract(address=tm.functions.collateral_token().call(), abi=ERC20_ABI)
    borr_token = bot.w3.eth.contract(address=tm.functions.borrow_token().call(), abi=ERC20_ABI)
    coll_sym, coll_dec, borr_sym, borr_dec = multicall(
        bot.w3,
        [
            coll_token.functions.symbol(),
            coll_token.functions.decimals(),
            borr_token.functions.symbol(),
            borr_token.functions.decimals(),
        ],
    )

    await post_event(
        bot,
        f"🔒 <b>Trove Closed</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Collateral:</b> {fmt(collateral / (10**coll_dec))} {coll_sym}\n"
        f"<b>Debt:</b> {fmt(debt / (10**borr_dec))} {borr_sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>",
        owner,
    )


async def on_close_zombie_trove(bot: TinyBot, log: object) -> None:
    trove_id: int = log.args.trove_id
    owner: str = log.args.trove_owner
    collateral: int = log.args.collateral_amount
    debt: int = log.args.debt_amount

    tm = bot.w3.eth.contract(address=log.address, abi=TROVE_MANAGER_ABI)
    coll_token = bot.w3.eth.contract(address=tm.functions.collateral_token().call(), abi=ERC20_ABI)
    borr_token = bot.w3.eth.contract(address=tm.functions.borrow_token().call(), abi=ERC20_ABI)
    coll_sym, coll_dec, borr_sym, borr_dec = multicall(
        bot.w3,
        [
            coll_token.functions.symbol(),
            coll_token.functions.decimals(),
            borr_token.functions.symbol(),
            borr_token.functions.decimals(),
        ],
    )

    await post_event(
        bot,
        f"🧟 <b>Zombie Trove Closed</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Collateral:</b> {fmt(collateral / (10**coll_dec))} {coll_sym}\n"
        f"<b>Debt:</b> {fmt(debt / (10**borr_dec))} {borr_sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>",
        owner,
    )


async def on_add_collateral(bot: TinyBot, log: object) -> None:
    trove_id: int = log.args.trove_id
    owner: str = log.args.trove_owner
    amount: int = log.args.collateral_amount

    tm = bot.w3.eth.contract(address=log.address, abi=TROVE_MANAGER_ABI)
    coll_token = bot.w3.eth.contract(address=tm.functions.collateral_token().call(), abi=ERC20_ABI)
    sym, dec = multicall(bot.w3, [coll_token.functions.symbol(), coll_token.functions.decimals()])

    await post_event(
        bot,
        f"💰 <b>Collateral Added</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Amount:</b> {fmt(amount / (10**dec))} {sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>",
        owner,
    )


async def on_remove_collateral(bot: TinyBot, log: object) -> None:
    trove_id: int = log.args.trove_id
    owner: str = log.args.trove_owner
    amount: int = log.args.collateral_amount

    tm = bot.w3.eth.contract(address=log.address, abi=TROVE_MANAGER_ABI)
    coll_token = bot.w3.eth.contract(address=tm.functions.collateral_token().call(), abi=ERC20_ABI)
    sym, dec = multicall(bot.w3, [coll_token.functions.symbol(), coll_token.functions.decimals()])

    await post_event(
        bot,
        f"💳 <b>Collateral Removed</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Amount:</b> {fmt(amount / (10**dec))} {sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>",
        owner,
    )


async def on_borrow(bot: TinyBot, log: object) -> None:
    trove_id: int = log.args.trove_id
    owner: str = log.args.trove_owner
    debt: int = log.args.debt_amount
    upfront_fee: int = log.args.upfront_fee

    tm = bot.w3.eth.contract(address=log.address, abi=TROVE_MANAGER_ABI)
    borr_token = bot.w3.eth.contract(address=tm.functions.borrow_token().call(), abi=ERC20_ABI)
    sym, dec = multicall(bot.w3, [borr_token.functions.symbol(), borr_token.functions.decimals()])

    await post_event(
        bot,
        f"💸 <b>Borrowed</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Amount:</b> {fmt(debt / (10**dec))} {sym}\n"
        f"<b>Upfront Fee:</b> {fmt(upfront_fee / (10**dec))} {sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>",
        owner,
    )


async def on_repay(bot: TinyBot, log: object) -> None:
    trove_id: int = log.args.trove_id
    owner: str = log.args.trove_owner
    debt: int = log.args.debt_amount

    tm = bot.w3.eth.contract(address=log.address, abi=TROVE_MANAGER_ABI)
    borr_token = bot.w3.eth.contract(address=tm.functions.borrow_token().call(), abi=ERC20_ABI)
    sym, dec = multicall(bot.w3, [borr_token.functions.symbol(), borr_token.functions.decimals()])

    await post_event(
        bot,
        f"💼 <b>Repaid</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Amount:</b> {fmt(debt / (10**dec))} {sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>",
        owner,
    )


async def on_adjust_interest_rate(bot: TinyBot, log: object) -> None:
    trove_id: int = log.args.trove_id
    owner: str = log.args.trove_owner
    rate: int = log.args.new_annual_interest_rate
    upfront_fee: int = log.args.upfront_fee

    tm = bot.w3.eth.contract(address=log.address, abi=TROVE_MANAGER_ABI)
    borr_token = bot.w3.eth.contract(address=tm.functions.borrow_token().call(), abi=ERC20_ABI)
    sym, dec = multicall(bot.w3, [borr_token.functions.symbol(), borr_token.functions.decimals()])
    old_rate = tm.functions.troves(trove_id).call(block_identifier=log.blockNumber - 1)[2]

    await post_event(
        bot,
        f"⚖️ <b>Interest Rate Adjusted</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Old Rate:</b> {old_rate / (10 ** (dec - 2)):.2f}%\n"
        f"<b>New Rate:</b> {rate / (10 ** (dec - 2)):.2f}%\n"
        f"<b>Upfront Fee:</b> {fmt(upfront_fee / (10**dec))} {sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>",
        owner,
    )


async def on_liquidate_trove(bot: TinyBot, log: object) -> None:
    trove_id: int = log.args.trove_id
    owner: str = log.args.trove_owner
    liquidator: str = log.args.liquidator
    collateral: int = log.args.collateral_amount
    debt: int = log.args.debt_amount
    is_full: bool = log.args.is_full_liquidation

    tm = bot.w3.eth.contract(address=log.address, abi=TROVE_MANAGER_ABI)
    coll_token = bot.w3.eth.contract(address=tm.functions.collateral_token().call(), abi=ERC20_ABI)
    borr_token = bot.w3.eth.contract(address=tm.functions.borrow_token().call(), abi=ERC20_ABI)
    coll_sym, coll_dec, borr_sym, borr_dec = multicall(
        bot.w3,
        [
            coll_token.functions.symbol(),
            coll_token.functions.decimals(),
            borr_token.functions.symbol(),
            borr_token.functions.decimals(),
        ],
    )

    status = "Full" if is_full else "Partial"
    await post_event(
        bot,
        f"💦 <b>{status} Liquidation!</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Liquidator:</b> {safe_name(bot.w3, liquidator, shorten=True)}\n"
        f"<b>Collateral:</b> {fmt(collateral / (10**coll_dec))} {coll_sym}\n"
        f"<b>Debt:</b> {fmt(debt / (10**borr_dec))} {borr_sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>",
        owner,
    )


async def on_redeem_trove(bot: TinyBot, log: object) -> None:
    trove_id: int = log.args.trove_id
    owner: str = log.args.trove_owner
    redeemer: str = log.args.redeemer
    collateral: int = log.args.collateral_amount
    debt: int = log.args.debt_amount

    tm = bot.w3.eth.contract(address=log.address, abi=TROVE_MANAGER_ABI)
    coll_token = bot.w3.eth.contract(address=tm.functions.collateral_token().call(), abi=ERC20_ABI)
    borr_token = bot.w3.eth.contract(address=tm.functions.borrow_token().call(), abi=ERC20_ABI)
    coll_sym, coll_dec, borr_sym, borr_dec = multicall(
        bot.w3,
        [
            coll_token.functions.symbol(),
            coll_token.functions.decimals(),
            borr_token.functions.symbol(),
            borr_token.functions.decimals(),
        ],
    )
    rate = tm.functions.troves(trove_id).call(block_identifier=log.blockNumber - 1)[2]

    await post_event(
        bot,
        f"😬 <b>Trove Redeemed</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Redeemer:</b> {safe_name(bot.w3, redeemer, shorten=True)}\n"
        f"<b>Collateral:</b> {fmt(collateral / (10**coll_dec))} {coll_sym}\n"
        f"<b>Debt:</b> {fmt(debt / (10**borr_dec))} {borr_sym}\n"
        f"<b>Rate:</b> {rate / (10 ** (borr_dec - 2)):.2f}%\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>",
        owner,
    )


async def on_redeem(bot: TinyBot, log: object) -> None:
    redeemer: str = log.args.redeemer
    collateral: int = log.args.collateral_amount
    debt: int = log.args.debt_amount

    tm = bot.w3.eth.contract(address=log.address, abi=TROVE_MANAGER_ABI)
    coll_token = bot.w3.eth.contract(address=tm.functions.collateral_token().call(), abi=ERC20_ABI)
    borr_token = bot.w3.eth.contract(address=tm.functions.borrow_token().call(), abi=ERC20_ABI)
    coll_sym, coll_dec, borr_sym, borr_dec = multicall(
        bot.w3,
        [
            coll_token.functions.symbol(),
            coll_token.functions.decimals(),
            borr_token.functions.symbol(),
            borr_token.functions.decimals(),
        ],
    )

    await notify_group_chat(
        f"🤠 <b>Redemption</b>\n\n"
        f"<b>Redeemer:</b> {safe_name(bot.w3, redeemer, shorten=True)}\n"
        f"<b>Collateral:</b> {fmt(collateral / (10**coll_dec))} {coll_sym}\n"
        f"<b>Debt:</b> {fmt(debt / (10**borr_dec))} {borr_sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
    )


# =============================================================================
# Auction Event Handlers
# =============================================================================


async def on_auction_kick(bot: TinyBot, log: object) -> None:
    auction_addr: str = log.address
    auction_id: int = log.args.auction_id
    kick_amount: int = log.args.kick_amount

    auction = bot.w3.eth.contract(address=auction_addr, abi=AUCTION_ABI)
    sell_token = bot.w3.eth.contract(address=auction.functions.sell_token().call(), abi=ERC20_ABI)
    sym, dec = multicall(bot.w3, [sell_token.functions.symbol(), sell_token.functions.decimals()])

    re_kick = "Re-Kicked" if log.args.is_re_kick else "Kicked"
    emoji = "🚨" if log.args.is_re_kick else "🥾"

    await notify_group_chat(
        f"{emoji} <b>Auction {re_kick}</b>\n\n"
        f"<b>Auction ID:</b> {short(auction_id)}\n"
        f"<b>Kick Amount:</b> {fmt(kick_amount / (10**dec), 4)} {sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
    )


async def on_auction_take(bot: TinyBot, log: object) -> None:
    auction_addr: str = log.address
    auction_id: int = log.args.auction_id
    take_amount: int = log.args.take_amount
    remaining: int = log.args.remaining_amount
    needed_amount: int = log.args.needed_amount
    tx_origin: str = bot.w3.eth.get_transaction(log.transactionHash)["from"]

    auction = bot.w3.eth.contract(address=auction_addr, abi=AUCTION_ABI)
    sell_token = bot.w3.eth.contract(address=auction.functions.sell_token().call(), abi=ERC20_ABI)
    buy_token = bot.w3.eth.contract(address=auction.functions.buy_token().call(), abi=ERC20_ABI)
    sell_sym, sell_dec, buy_sym, buy_dec = multicall(
        bot.w3,
        [
            sell_token.functions.symbol(),
            sell_token.functions.decimals(),
            buy_token.functions.symbol(),
            buy_token.functions.decimals(),
        ],
    )

    status = "fully taken" if remaining == 0 else "partially taken"
    remaining_line = "" if remaining == 0 else f"<b>Remaining:</b> {fmt(remaining / (10**sell_dec), 4)} {sell_sym}\n"
    await notify_group_chat(
        f"🎯 <b>Auction {status}!</b>\n\n"
        f"<b>Auction ID:</b> {short(auction_id)}\n"
        f"<b>Take Amount:</b> {fmt(take_amount / (10**sell_dec), 4)} {sell_sym}\n"
        f"<b>Paid:</b> {fmt(needed_amount / (10**buy_dec), 4)} {buy_sym}\n"
        f"{remaining_line}"
        f"<b>Taker:</b> {safe_name(bot.w3, tx_origin, shorten=True)}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
    )


# =============================================================================
# Lender Event Handlers
# =============================================================================


async def on_reported(bot: TinyBot, log: object) -> None:
    profit: int = log.args.profit
    loss: int = log.args.loss
    performance_fees: int = log.args.performanceFees

    lender = bot.w3.eth.contract(address=log.address, abi=LENDER_ABI)
    asset = bot.w3.eth.contract(address=lender.functions.asset().call(), abi=ERC20_ABI)
    sym, dec = multicall(bot.w3, [asset.functions.symbol(), asset.functions.decimals()])

    await notify_group_chat(
        f"✍🏻 <b>Lender Report</b>\n\n"
        f"<b>Lender:</b> {safe_name(bot.w3, log.address).replace('Flex ', '').replace(' Lender', '')}\n"
        f"<b>Profit:</b> {fmt(profit / (10**dec))} {sym}\n"
        f"<b>Loss:</b> {fmt(loss / (10**dec))} {sym}\n"
        f"<b>Performance Fees:</b> {fmt(performance_fees / (10**dec))} {sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
    )


async def on_deposit(bot: TinyBot, log: object) -> None:
    owner: str = log.args.owner
    assets: int = log.args.assets

    lender = bot.w3.eth.contract(address=log.address, abi=LENDER_ABI)
    asset = bot.w3.eth.contract(address=lender.functions.asset().call(), abi=ERC20_ABI)
    sym, dec = multicall(bot.w3, [asset.functions.symbol(), asset.functions.decimals()])

    await notify_group_chat(
        f"🔥 <b>Lender Deposit</b>\n\n"
        f"<b>Lender:</b> {safe_name(bot.w3, log.address).replace('Flex ', '').replace(' Lender', '')}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Assets:</b> {fmt(assets / (10**dec))} {sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
    )


async def on_withdraw(bot: TinyBot, log: object) -> None:
    owner: str = log.args.owner
    assets: int = log.args.assets

    lender = bot.w3.eth.contract(address=log.address, abi=LENDER_ABI)
    asset = bot.w3.eth.contract(address=lender.functions.asset().call(), abi=ERC20_ABI)
    sym, dec = multicall(bot.w3, [asset.functions.symbol(), asset.functions.decimals()])

    await notify_group_chat(
        f"👋 <b>Lender Withdrawal</b>\n\n"
        f"<b>Lender:</b> {safe_name(bot.w3, log.address).replace('Flex ', '').replace(' Lender', '')}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Assets:</b> {fmt(assets / (10**dec))} {sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
    )


# =============================================================================
# Registry & Factory Event Handlers
# =============================================================================


async def on_endorse_market(bot: TinyBot, log: object) -> None:
    trove_manager: str = log.args.trove_manager

    tm = bot.w3.eth.contract(address=bot.w3.to_checksum_address(trove_manager), abi=TROVE_MANAGER_ABI)
    coll_token = bot.w3.eth.contract(address=tm.functions.collateral_token().call(), abi=ERC20_ABI)
    borr_token = bot.w3.eth.contract(address=tm.functions.borrow_token().call(), abi=ERC20_ABI)
    coll_sym, borr_sym = multicall(bot.w3, [coll_token.functions.symbol(), borr_token.functions.symbol()])

    await notify_group_chat(
        f"✅ <b>Market Endorsed</b>\n\n"
        f"<b>Market:</b> {coll_sym}/{borr_sym}\n"
        f"<b>Trove Manager:</b> {short(trove_manager)}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
    )


async def on_unendorse_market(bot: TinyBot, log: object) -> None:
    trove_manager: str = log.args.trove_manager

    tm = bot.w3.eth.contract(address=bot.w3.to_checksum_address(trove_manager), abi=TROVE_MANAGER_ABI)
    coll_token = bot.w3.eth.contract(address=tm.functions.collateral_token().call(), abi=ERC20_ABI)
    borr_token = bot.w3.eth.contract(address=tm.functions.borrow_token().call(), abi=ERC20_ABI)
    coll_sym, borr_sym = multicall(bot.w3, [coll_token.functions.symbol(), borr_token.functions.symbol()])

    await notify_group_chat(
        f"❌ <b>Market Unendorsed</b>\n\n"
        f"<b>Market:</b> {coll_sym}/{borr_sym}\n"
        f"<b>Trove Manager:</b> {short(trove_manager)}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
    )


async def on_deploy_new_market(bot: TinyBot, log: object) -> None:
    deployer: str = log.args.deployer
    trove_manager: str = log.args.trove_manager

    tm = bot.w3.eth.contract(address=bot.w3.to_checksum_address(trove_manager), abi=TROVE_MANAGER_ABI)
    coll_token = bot.w3.eth.contract(address=tm.functions.collateral_token().call(), abi=ERC20_ABI)
    borr_token = bot.w3.eth.contract(address=tm.functions.borrow_token().call(), abi=ERC20_ABI)
    coll_sym, borr_sym = multicall(bot.w3, [coll_token.functions.symbol(), borr_token.functions.symbol()])

    await notify_group_chat(
        f"👀 <b>New Market Deployed</b>\n\n"
        f"<b>Market:</b> {coll_sym}/{borr_sym}\n"
        f"<b>Deployer:</b> {safe_name(bot.w3, deployer, shorten=True)}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
    )


# =============================================================================
# Periodic Tasks
# =============================================================================


async def _notify_report(bot: TinyBot, vault: str, strategy: str, tx_hash: str) -> None:
    await notify_group_chat(
        f"⚙️ <b>Reported</b>\n"
        f"<b>Vault:</b> {safe_name(bot.w3, vault, shorten=True)}\n"
        f"<b>Strategy:</b> {safe_name(bot.w3, strategy, shorten=True)}\n\n"
        f"<a href='{explorer_tx_url()}{tx_hash}'>🔗 View Transaction</a>",
        chat_id=DEV_GROUP_CHAT_ID,
    )


async def check_and_report(bot: TinyBot) -> None:
    base_fee_gwei = bot.w3.eth.get_block("latest").baseFeePerGas / 1e9
    if base_fee_gwei > MAX_GAS_GWEI:
        print(f"skipping report: base fee {base_fee_gwei:.2f} gwei > {MAX_GAS_GWEI}")
        return

    trigger = bot.w3.eth.contract(address=COMMON_REPORT_TRIGGER, abi=REPORT_TRIGGER_ABI)
    keeper = bot.w3.eth.contract(address=PERMISSIONLESS_KEEPER, abi=KEEPER_ABI)

    markets = get_all_markets(bot.w3)
    if markets:
        for lender in get_all_lenders(bot.w3, markets):
            should_report, _ = trigger.functions.strategyReportTrigger(lender).call()
            if should_report:
                tx_hash = bot.executor.execute(keeper.functions.report(lender), max_priority_fee_gwei=0.1)
                print(f"report tx sent for lender {lender}: {tx_hash}")

    vaults = allocator_vaults()
    if not vaults:
        return

    perm_keeper = bot.w3.eth.contract(address=PERMISSIONED_KEEPER, abi=PERMISSIONED_KEEPER_ABI)
    if not perm_keeper.functions.keepers(bot.executor.address).call():
        print(f"skipping allocator reports: {bot.executor.address} is not a keeper on {PERMISSIONED_KEEPER}")
        return

    for vault_addr in vaults:
        vault = bot.w3.eth.contract(address=vault_addr, abi=ALLOCATOR_VAULT_ABI)
        for strategy in vault.functions.get_default_queue().call():
            should_strategy, _ = trigger.functions.strategyReportTrigger(strategy).call()
            if should_strategy:
                tx_hash = bot.executor.execute(perm_keeper.functions.harvestStrategy(strategy), max_priority_fee_gwei=0.1)
                await _notify_report(bot, vault_addr, strategy, tx_hash)

            should_vault, _ = trigger.functions.vaultReportTrigger(vault_addr, strategy).call()
            if should_vault:
                tx_hash = bot.executor.execute(
                    perm_keeper.functions.processReport(vault_addr, strategy), max_priority_fee_gwei=0.1
                )
                await _notify_report(bot, vault_addr, strategy, tx_hash)


async def backup_alerts(bot: TinyBot) -> None:
    await asyncio.to_thread(bot.store.flush)


# =============================================================================
# Main
# =============================================================================


async def run() -> None:
    bot = TinyBot(
        rpc_url=os.environ["RPC_URL"],
        name=f"📡 {network()} flex monitor",
        private_key=os.environ["KEEPER_PRIVATE_KEY"],
    )
    github = (
        {"repo": GITHUB_REPO, "path": GITHUB_BACKUP_PATH, "branch": GITHUB_BACKUP_BRANCH, "token": GITHUB_TOKEN}
        if GITHUB_TOKEN and GITHUB_REPO
        else None
    )
    bot.store = Store(ALERTS_STATE_PATH, github=github)

    markets = get_all_markets(bot.w3)
    lenders = get_all_lenders(bot.w3, markets)
    auctions = get_all_auctions(bot.w3, markets)

    # Trove Manager events
    trove_events = {
        "OpenTrove": on_open_trove,
        "CloseTrove": on_close_trove,
        "CloseZombieTrove": on_close_zombie_trove,
        "AddCollateral": on_add_collateral,
        "RemoveCollateral": on_remove_collateral,
        "Borrow": on_borrow,
        "Repay": on_repay,
        "AdjustInterestRate": on_adjust_interest_rate,
        "LiquidateTrove": on_liquidate_trove,
        "RedeemTrove": on_redeem_trove,
        "Redeem": on_redeem,
    }
    if markets:
        for event, handler in trove_events.items():
            bot.listen(poll_interval=INTERVAL, event=event, addresses=markets, abi=TROVE_MANAGER_ABI, handler=handler)

    # Lender events
    lender_events = {
        "Reported": on_reported,
        "Deposit": on_deposit,
        "Withdraw": on_withdraw,
    }
    if lenders:
        for event, handler in lender_events.items():
            bot.listen(poll_interval=INTERVAL, event=event, addresses=lenders, abi=LENDER_ABI, handler=handler)

    # Auction events
    auction_events = {
        "AuctionKick": on_auction_kick,
        "AuctionTake": on_auction_take,
    }
    if auctions:
        for event, handler in auction_events.items():
            bot.listen(poll_interval=INTERVAL, event=event, addresses=auctions, abi=AUCTION_ABI, handler=handler)

    # Registry events
    bot.listen(
        poll_interval=INTERVAL,
        event="EndorseMarket",
        addresses=[registry_addr()],
        abi=REGISTRY_ABI,
        handler=on_endorse_market,
    )
    bot.listen(
        poll_interval=INTERVAL,
        event="UnendorseMarket",
        addresses=[registry_addr()],
        abi=REGISTRY_ABI,
        handler=on_unendorse_market,
    )

    # Factory events
    bot.listen(
        poll_interval=INTERVAL,
        event="DeployNewMarket",
        addresses=[factory_addr()],
        abi=FACTORY_ABI,
        handler=on_deploy_new_market,
    )

    # Periodic: check & report strategies hourly
    bot.every(REPORT_INTERVAL, check_and_report)

    # Periodic: back up alerts state to GitHub (~daily)
    if GITHUB_TOKEN and GITHUB_REPO:
        bot.every(BACKUP_INTERVAL, backup_alerts)

    # # TEST Trove Manager
    # await bot.replay("on_open_trove", from_block=25179201, to_block=25179204)
    # await bot.replay("on_close_trove", from_block=24743415, to_block=24743417)
    # await bot.replay("on_close_zombie_trove", from_block=24750530, to_block=24750532)
    # await bot.replay("on_add_collateral", from_block=24742696, to_block=24742698)
    # await bot.replay("on_remove_collateral", from_block=24743344, to_block=24743346)
    # await bot.replay("on_borrow", from_block=24743349, to_block=24743351)
    # await bot.replay("on_repay", from_block=24743354, to_block=24743356)
    # await bot.replay("on_adjust_interest_rate", from_block=24743358, to_block=24743360)
    # await bot.replay("on_liquidate_trove", from_block=24750633, to_block=24750635)
    # await bot.replay("on_redeem_trove", from_block=24750980, to_block=24750981)
    # await bot.replay("on_redeem", from_block=24750980, to_block=24750982)
    # await bot.replay("on_pending_ownership_transfer", from_block=24750633, to_block=24750635)
    # await bot.replay("on_ownership_transferred", from_block=24750633, to_block=24750635)

    # # TEST Lender
    # await bot.replay("on_reported", from_block=24742508, to_block=24742510)
    # await bot.replay("on_deposit", from_block=24737555, to_block=24737557)
    # await bot.replay("on_withdraw", from_block=24743460, to_block=24743462)

    # # TEST Auction
    # await bot.replay("on_auction_kick", from_block=24750789, to_block=24750791)
    # await bot.replay("on_auction_take", from_block=24750633, to_block=24750635)

    # # TEST Registry
    # await bot.replay("on_endorse_market", from_block=24737203, to_block=24737205)
    # await bot.replay("on_unendorse_market", from_block=24750633, to_block=24750635)

    # # TEST Factory
    # await bot.replay("on_deploy_new_market", from_block=24737201, to_block=24737203)

    await asyncio.gather(bot.run(), telegram_command_loop(bot))
