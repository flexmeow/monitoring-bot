import os

from tinybot import TinyBot, multicall, notify_group_chat

from bot.config import (
    AUCTION_ABI,
    ERC20_ABI,
    FACTORY_ABI,
    INTERVAL,
    LENDER_ABI,
    REGISTRY_ABI,
    TROVE_MANAGER_ABI,
    explorer_tx_url,
    factory_addr,
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

    await notify_group_chat(
        f"🏦 <b>Trove Opened</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Collateral:</b> {collateral / (10**coll_dec):.2f} {coll_sym}\n"
        f"<b>Debt:</b> {debt / (10**borr_dec):.2f} {borr_sym}\n"
        f"<b>Upfront Fee:</b> {upfront_fee / (10**borr_dec):.2f} {borr_sym}\n"
        f"<b>Interest Rate:</b> {rate / (10 ** (borr_dec - 2)):.2f}%\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
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

    await notify_group_chat(
        f"🔒 <b>Trove Closed</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Collateral:</b> {collateral / (10**coll_dec):.2f} {coll_sym}\n"
        f"<b>Debt:</b> {debt / (10**borr_dec):.2f} {borr_sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
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

    await notify_group_chat(
        f"🧟 <b>Zombie Trove Closed</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Collateral:</b> {collateral / (10**coll_dec):.2f} {coll_sym}\n"
        f"<b>Debt:</b> {debt / (10**borr_dec):.2f} {borr_sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
    )


async def on_add_collateral(bot: TinyBot, log: object) -> None:
    trove_id: int = log.args.trove_id
    owner: str = log.args.trove_owner
    amount: int = log.args.collateral_amount

    tm = bot.w3.eth.contract(address=log.address, abi=TROVE_MANAGER_ABI)
    coll_token = bot.w3.eth.contract(address=tm.functions.collateral_token().call(), abi=ERC20_ABI)
    sym, dec = multicall(bot.w3, [coll_token.functions.symbol(), coll_token.functions.decimals()])

    await notify_group_chat(
        f"💰 <b>Collateral Added</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Amount:</b> {amount / (10**dec):.2f} {sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
    )


async def on_remove_collateral(bot: TinyBot, log: object) -> None:
    trove_id: int = log.args.trove_id
    owner: str = log.args.trove_owner
    amount: int = log.args.collateral_amount

    tm = bot.w3.eth.contract(address=log.address, abi=TROVE_MANAGER_ABI)
    coll_token = bot.w3.eth.contract(address=tm.functions.collateral_token().call(), abi=ERC20_ABI)
    sym, dec = multicall(bot.w3, [coll_token.functions.symbol(), coll_token.functions.decimals()])

    await notify_group_chat(
        f"💳 <b>Collateral Removed</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Amount:</b> {amount / (10**dec):.2f} {sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
    )


async def on_borrow(bot: TinyBot, log: object) -> None:
    trove_id: int = log.args.trove_id
    owner: str = log.args.trove_owner
    debt: int = log.args.debt_amount
    upfront_fee: int = log.args.upfront_fee

    tm = bot.w3.eth.contract(address=log.address, abi=TROVE_MANAGER_ABI)
    borr_token = bot.w3.eth.contract(address=tm.functions.borrow_token().call(), abi=ERC20_ABI)
    sym, dec = multicall(bot.w3, [borr_token.functions.symbol(), borr_token.functions.decimals()])

    await notify_group_chat(
        f"💸 <b>Borrowed</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Amount:</b> {debt / (10**dec):.2f} {sym}\n"
        f"<b>Upfront Fee:</b> {upfront_fee / (10**dec):.2f} {sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
    )


async def on_repay(bot: TinyBot, log: object) -> None:
    trove_id: int = log.args.trove_id
    owner: str = log.args.trove_owner
    debt: int = log.args.debt_amount

    tm = bot.w3.eth.contract(address=log.address, abi=TROVE_MANAGER_ABI)
    borr_token = bot.w3.eth.contract(address=tm.functions.borrow_token().call(), abi=ERC20_ABI)
    sym, dec = multicall(bot.w3, [borr_token.functions.symbol(), borr_token.functions.decimals()])

    await notify_group_chat(
        f"💼 <b>Repaid</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Amount:</b> {debt / (10**dec):.2f} {sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
    )


async def on_adjust_interest_rate(bot: TinyBot, log: object) -> None:
    trove_id: int = log.args.trove_id
    owner: str = log.args.trove_owner
    rate: int = log.args.new_annual_interest_rate
    upfront_fee: int = log.args.upfront_fee

    tm = bot.w3.eth.contract(address=log.address, abi=TROVE_MANAGER_ABI)
    borr_token = bot.w3.eth.contract(address=tm.functions.borrow_token().call(), abi=ERC20_ABI)
    sym, dec = multicall(bot.w3, [borr_token.functions.symbol(), borr_token.functions.decimals()])

    await notify_group_chat(
        f"⚖️ <b>Interest Rate Adjusted</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>New Rate:</b> {rate / (10 ** (dec - 2)):.2f}%\n"
        f"<b>Upfront Fee:</b> {upfront_fee / (10**dec):.2f} {sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
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
    await notify_group_chat(
        f"💦 <b>{status} Liquidation!</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Liquidator:</b> {safe_name(bot.w3, liquidator, shorten=True)}\n"
        f"<b>Collateral:</b> {collateral / (10**coll_dec):.2f} {coll_sym}\n"
        f"<b>Debt:</b> {debt / (10**borr_dec):.2f} {borr_sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
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

    await notify_group_chat(
        f"😬 <b>Trove Redeemed</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>Owner:</b> {safe_name(bot.w3, owner, shorten=True)}\n"
        f"<b>Redeemer:</b> {safe_name(bot.w3, redeemer, shorten=True)}\n"
        f"<b>Collateral:</b> {collateral / (10**coll_dec):.2f} {coll_sym}\n"
        f"<b>Debt:</b> {debt / (10**borr_dec):.2f} {borr_sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
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
        f"<b>Collateral:</b> {collateral / (10**coll_dec):.2f} {coll_sym}\n"
        f"<b>Debt:</b> {debt / (10**borr_dec):.2f} {borr_sym}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
    )


async def on_pending_ownership_transfer(bot: TinyBot, log: object) -> None:
    trove_id: int = log.args.trove_id
    old_owner: str = log.args.old_owner
    new_owner: str = log.args.new_owner

    await notify_group_chat(
        f"🔑 <b>Pending Ownership Transfer</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>From:</b> {safe_name(bot.w3, old_owner, shorten=True)}\n"
        f"<b>To:</b> {safe_name(bot.w3, new_owner, shorten=True)}\n\n"
        f"<a href='{explorer_tx_url()}{log.transactionHash.hex()}'>🔗 View Transaction</a>"
    )


async def on_ownership_transferred(bot: TinyBot, log: object) -> None:
    trove_id: int = log.args.trove_id
    old_owner: str = log.args.old_owner
    new_owner: str = log.args.new_owner

    await notify_group_chat(
        f"🔑 <b>Ownership Transferred</b>\n\n"
        f"<b>Trove ID:</b> {short(trove_id)}\n"
        f"<b>From:</b> {safe_name(bot.w3, old_owner, shorten=True)}\n"
        f"<b>To:</b> {safe_name(bot.w3, new_owner, shorten=True)}\n\n"
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
        f"<b>Kick Amount:</b> {kick_amount / (10**dec):.4f} {sym}\n\n"
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
    remaining_line = "" if remaining == 0 else f"<b>Remaining:</b> {remaining / (10**sell_dec):.4f} {sell_sym}\n"
    await notify_group_chat(
        f"🎯 <b>Auction {status}!</b>\n\n"
        f"<b>Auction ID:</b> {short(auction_id)}\n"
        f"<b>Take Amount:</b> {take_amount / (10**sell_dec):.4f} {sell_sym}\n"
        f"<b>Paid:</b> {needed_amount / (10**buy_dec):.4f} {buy_sym}\n"
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
        f"<b>Profit:</b> {profit / (10**dec):.2f} {sym}\n"
        f"<b>Loss:</b> {loss / (10**dec):.2f} {sym}\n"
        f"<b>Performance Fees:</b> {performance_fees / (10**dec):.2f} {sym}\n\n"
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
        f"<b>Assets:</b> {assets / (10**dec):.2f} {sym}\n\n"
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
        f"<b>Assets:</b> {assets / (10**dec):.2f} {sym}\n\n"
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
# Main
# =============================================================================


async def run() -> None:
    bot = TinyBot(
        rpc_url=os.environ["RPC_URL"],
        name=f"📡 {network()} flex monitor",
    )

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
        "PendingOwnershipTransfer": on_pending_ownership_transfer,
        "OwnershipTransferred": on_ownership_transferred,
    }
    for event, handler in trove_events.items():
        bot.listen(poll_interval=INTERVAL, event=event, addresses=markets, abi=TROVE_MANAGER_ABI, handler=handler)

    # Lender events
    lender_events = {
        "Reported": on_reported,
        "Deposit": on_deposit,
        "Withdraw": on_withdraw,
    }
    for event, handler in lender_events.items():
        bot.listen(poll_interval=INTERVAL, event=event, addresses=lenders, abi=LENDER_ABI, handler=handler)

    # Auction events
    auction_events = {
        "AuctionKick": on_auction_kick,
        "AuctionTake": on_auction_take,
    }
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

    # # # TEST Trove Manager
    # await bot.replay("on_open_trove", from_block=24750608, to_block=24750610)
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

    await bot.run()
