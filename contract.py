import smartpy as sp


# The enum used for the contract related errors.
#
class Error:

    # The contract function is not accessible for the sender.
    ACCESS_DENIED = "OD_ACCESS_DENIED"

    # The corresponding argument value is invalid.
    ILLEGAL_ARGUMENT = "OD_ILLEGAL_ARGUMENT"

    # The corresponding transaction has incorrect tezos amount.
    ILLEGAL_TX_AMOUNT = "OD_ILLEGAL_TX_AMOUNT"

    # The contract is paused.
    PAUSED = "OD_PAUSED"



#########################################################################################################
# The contract is a storage for p2p credit deals and provides service functionality to make such deals. #
#########################################################################################################
class Opus(sp.Contract):
    def __init__(self, creator):
        self.creator = creator

        self.init(
            # indicates that making of credit deals is disabled
            # (if the value is True, creating loan requests and making deals are not possible)
            pause = False,

            # baker address or None
            baker = sp.none,

            # list of admin addresses
            admins = sp.set([creator]),

            # supported tokens (list of pairs: token name and token address)
            tokens = sp.big_map(tkey = sp.TString, tvalue = sp.TAddress),

            # time bounds for credit deals
            time = sp.record(min = sp.nat(7 * 86400), max = sp.nat(180 * 86400)),

            # minimum deposit value
            min_deposit = sp.tez(1),

            # service fee (APY) in basis points
            fee = sp.nat(100),

            # last loan request ID
            nloan = sp.nat(0),

            # last credit deal ID
            ndeal = sp.nat(0),

            # map of loan requests (key is loan request ID)
            loans = sp.big_map(),

            # map of credit deals (key is credit deal ID)
            deals = sp.big_map(),

            # amount of locked collateral
            deposits = sp.mutez(0)
        )


    # Support tezos transfer to the contract address
    #
    @sp.entry_point
    def default(self):
        pass


    # (Admins only) Transfer tezos (except locked collateral) from the contract address.
    # @params.address – destination address
    # @params.amount – tezos amount
    #
    @sp.entry_point
    def withdraw(self, params):
        sp.set_type(params.address, sp.TAddress)
        sp.set_type(params.amount, sp.TMutez)
        sp.verify(self.data.admins.contains(sp.sender), message = Error.ACCESS_DENIED)
        sp.verify(params.amount > sp.mutez(0), message = Error.ILLEGAL_ARGUMENT + ":amount")
        sp.verify((sp.balance - self.data.deposits) >= params.amount, message = Error.ILLEGAL_ARGUMENT + ":amount")
        sp.send(params.address, params.amount)


    # (Admins only) Add an admin address to the list of admin addresses.
    # @params.address – new admin address
    #
    @sp.entry_point
    def add_admin(self, params):
        sp.set_type(params.address, sp.TAddress)
        sp.verify(sp.amount == sp.mutez(0), message = Error.ILLEGAL_TX_AMOUNT)
        sp.verify(self.data.admins.contains(sp.sender), message = Error.ACCESS_DENIED)
        sp.verify(~self.data.admins.contains(params.address), message = Error.ILLEGAL_ARGUMENT + ":address")
        self.data.admins.add(params.address)


    # (Admins only) Remove an admin address from the list of admin addresses.
    # @params.address – admin address
    #
    @sp.entry_point
    def remove_admin(self, params):
        sp.set_type(params.address, sp.TAddress)
        sp.verify(sp.amount == sp.mutez(0), message = Error.ILLEGAL_TX_AMOUNT)
        sp.verify(self.data.admins.contains(sp.sender), message = Error.ACCESS_DENIED)
        sp.verify(self.creator != params.address, message = Error.ILLEGAL_ARGUMENT + ":address")
        sp.verify(self.data.admins.contains(params.address), message = Error.ILLEGAL_ARGUMENT + ":address")
        self.data.admins.remove(params.address)


    # (Admins only) Disable/enable making of new loan requests and new deals.
    # @params.pause – True or False
    #
    @sp.entry_point
    def pause(self, params):
        sp.set_type(params.pause, sp.TBool)
        sp.verify(sp.amount == sp.mutez(0), message = Error.ILLEGAL_TX_AMOUNT)
        sp.verify(self.data.admins.contains(sp.sender), message = Error.ACCESS_DENIED)
        sp.verify(self.data.pause != params.pause, message = Error.ILLEGAL_ARGUMENT + ":pause")
        self.data.pause = params.pause


    # (Admins only) Set a baker for the contract.
    # @params.baker – baker address or None
    #
    @sp.entry_point
    def delegate(self, params):
        sp.set_type(params.baker, sp.TOption(sp.TKeyHash))
        sp.verify(sp.amount == sp.mutez(0), message = Error.ILLEGAL_TX_AMOUNT)
        sp.verify(self.data.admins.contains(sp.sender), message = Error.ACCESS_DENIED)
        sp.verify(self.data.baker != params.baker, message = Error.ILLEGAL_ARGUMENT + ":baker")
        self.data.baker = params.baker
        sp.set_delegate(params.baker)


    # (Admins only) Add supported token.
    # @params.name – token name
    # @params.address – token address
    #
    @sp.entry_point
    def add_token(self, params):
        sp.set_type(params.name, sp.TString)
        sp.set_type(params.address, sp.TAddress)
        sp.verify(sp.amount == sp.mutez(0), message = Error.ILLEGAL_TX_AMOUNT)
        sp.verify(self.data.admins.contains(sp.sender), message = Error.ACCESS_DENIED)
        self.data.tokens[params.name] = params.address


    # (Admins only) Remove supported token.
    # @params.name – token name
    #
    @sp.entry_point
    def remove_token(self, params):
        sp.set_type(params.name, sp.TString)
        sp.verify(sp.amount == sp.mutez(0), message = Error.ILLEGAL_TX_AMOUNT)
        sp.verify(self.data.admins.contains(sp.sender), message = Error.ACCESS_DENIED)
        sp.verify(self.data.tokens.contains(params.name), message = Error.ILLEGAL_ARGUMENT + ":name")
        del self.data.tokens[params.name]


    # (Admins only) Set a service fee.
    # @params.fee – fee value (APY) in basis points
    #
    @sp.entry_point
    def set_fee(self, params):
        sp.set_type(params.fee, sp.TNat)
        sp.verify(sp.amount == sp.mutez(0), message = Error.ILLEGAL_TX_AMOUNT)
        sp.verify(self.data.admins.contains(sp.sender), message = Error.ACCESS_DENIED)
        sp.verify(self.data.fee != params.fee, message = Error.ILLEGAL_ARGUMENT + ":fee")
        sp.verify(params.fee < 10000, message = Error.ILLEGAL_ARGUMENT + ":fee")
        self.data.fee = params.fee


    # (Admins only) Set minimum deposit value for loan requests.
    # @params.min_deposit – minimum deposit value
    #
    @sp.entry_point
    def set_min_deposit(self, params):
        sp.set_type(params.min_deposit, sp.TMutez)
        sp.verify(sp.amount == sp.mutez(0), message = Error.ILLEGAL_TX_AMOUNT)
        sp.verify(self.data.admins.contains(sp.sender), message = Error.ACCESS_DENIED)
        sp.verify(self.data.min_deposit != params.min_deposit, message = Error.ILLEGAL_ARGUMENT + ":min_deposit")
        self.data.min_deposit = params.min_deposit


    # (Admins only) Set time bounds for credit deals.
    # @params.min – minimum deal duration in seconds
    # @params.max – maximum deal duration in seconds
    #
    @sp.entry_point
    def set_time(self, params):
        sp.set_type(params, sp.TRecord(min = sp.TNat, max = sp.TNat))
        sp.verify(sp.amount == sp.mutez(0), message = Error.ILLEGAL_TX_AMOUNT)
        sp.verify(self.data.admins.contains(sp.sender), message = Error.ACCESS_DENIED)
        sp.verify(self.data.time != params, message = Error.ILLEGAL_ARGUMENT + ":min,max")
        sp.verify((params.min > 0) & (params.min <= params.max), message = Error.ILLEGAL_ARGUMENT + ":min")
        self.data.time = params


    # Create a new loan request.
    # The corresponding transaction amount has to include deposit and service fee.
    # @params.token – token name
    # @params.token_address – token address
    # @params.amount – requested amount of tokens
    # @params.reward – amount of tokens as creditor's reward 
    # @params.deposit – deposit amount, the sender has to send the same amount of tezos
    # @params.time – credit deal duration in seconds
    # @params.validity – loan request expire date or None
    #
    @sp.entry_point
    def add_loan(self, params):
        sp.set_type(params.token, sp.TString)
        sp.set_type(params.token_address, sp.TAddress)
        sp.set_type(params.amount, sp.TNat)
        sp.set_type(params.reward, sp.TNat)
        sp.set_type(params.deposit, sp.TMutez)
        sp.set_type(params.time, sp.TNat)
        sp.set_type(params.validity, sp.TOption(sp.TTimestamp))
        sp.verify(~self.data.pause, message = Error.PAUSED)
        sp.verify(self.data.tokens.contains(params.token), message = Error.ILLEGAL_ARGUMENT + ":token")
        sp.verify(self.data.tokens[params.token] == params.token_address, message = Error.ILLEGAL_ARGUMENT + ":token_address")
        sp.verify(params.amount > 0, message = Error.ILLEGAL_ARGUMENT + ":amount")
        sp.verify(params.deposit >= self.data.min_deposit, message = Error.ILLEGAL_ARGUMENT + ":deposit")
        sp.verify((params.time >= self.data.time.min) & (params.time <= self.data.time.max), message = Error.ILLEGAL_ARGUMENT + ":time")
        sp.verify((params.validity == sp.none) | (params.validity > sp.some(sp.now)), message = Error.ILLEGAL_ARGUMENT + ":validity")
        # Service fee calculation
        f = sp.local("f", sp.utils.nat_to_mutez(sp.utils.mutez_to_nat(params.deposit) * params.time * self.data.fee // (3600 * 24 * 365 * 100 * 100)))
        sp.verify(sp.amount == (params.deposit + f.value), message = Error.ILLEGAL_TX_AMOUNT)
        loan = sp.record(
            ts = sp.now,
            borrower = sp.sender,
            validity = params.validity,
            amount = params.amount,
            token = params.token,
            token_address = self.data.tokens[params.token],
            time = params.time,
            reward = params.reward,
            deposit = params.deposit,
            fee = f.value
        )
        self.data.nloan += 1
        self.data.loans[self.data.nloan] = loan
        self.data.deposits += sp.amount


    # Cancel sender's loan request, deposit and fee of the loan are returned to the sender.
    # @params.id – loan request ID
    #
    @sp.entry_point
    def cancel_loan(self, params):
        sp.set_type(params.id, sp.TNat)
        sp.verify(sp.amount == sp.mutez(0), message = Error.ILLEGAL_TX_AMOUNT)
        sp.verify(self.data.loans.contains(params.id), message = Error.ILLEGAL_ARGUMENT + ":id")
        loan = sp.local("loan", self.data.loans[params.id])
        sp.verify((sp.sender == loan.value.borrower) | self.data.admins.contains(sp.sender), Error.ACCESS_DENIED)
        sp.if loan.value.deposit > sp.mutez(0):
            sp.send(loan.value.borrower, loan.value.deposit + loan.value.fee)
            self.data.deposits -= (loan.value.deposit + loan.value.fee)
        del self.data.loans[params.id]


    # Make a credit deal, the sender has to approve the corresponding token transfer early.
    # @params.id – loan request ID
    #
    @sp.entry_point
    def make_deal(self, params):
        sp.set_type(params.id, sp.TNat)
        sp.verify(~self.data.pause, message = Error.PAUSED)
        sp.verify(sp.amount == sp.mutez(0), message = Error.ILLEGAL_TX_AMOUNT)
        sp.verify(self.data.loans.contains(params.id), message = Error.ILLEGAL_ARGUMENT + ":id")
        loan = sp.local("loan", self.data.loans[params.id])
        sp.verify(loan.value.borrower != sp.sender, Error.ILLEGAL_ARGUMENT + ":sender")
        sp.verify((loan.value.validity == sp.none) | (loan.value.validity > sp.some(sp.now)), message = Error.ILLEGAL_ARGUMENT + ":now")
        deal = sp.record(
            ts = sp.now,
            borrower = loan.value.borrower,
            creditor = sp.sender,
            amount = loan.value.amount,
            token = loan.value.token,
            token_address = loan.value.token_address,
            exp = sp.now.add_seconds(sp.to_int(loan.value.time)),
            reward = loan.value.reward,
            deposit = loan.value.deposit,
        )
        self.transfer_tokens(f=sp.sender, t=loan.value.borrower, v=loan.value.amount, token_address=loan.value.token_address)
        self.data.ndeal += 1
        self.data.deals[self.data.ndeal] = deal
        self.data.deposits -= loan.value.fee
        del self.data.loans[params.id]


    # Close a deal by borrower or creditor/admins.
    # If a deal is closed by borrower, the tokens are sent to the creditor and the borrower gets back the deposit;
    # if a deal timed out and it's closed by the creditor or admins, the creditor gets the deposit.
    # @params.id – credit deal ID
    #
    @sp.entry_point
    def close_deal(self, params):
        sp.set_type(params.id, sp.TNat)
        sp.verify(sp.amount == sp.mutez(0), message = Error.ILLEGAL_TX_AMOUNT)
        sp.verify(self.data.deals.contains(params.id), message = Error.ILLEGAL_ARGUMENT + ":id")
        deal = sp.local("deal", self.data.deals[params.id])
        sp.verify((sp.sender == deal.value.borrower) | (sp.sender == deal.value.creditor) | self.data.admins.contains(sp.sender), Error.ACCESS_DENIED)
        sp.if sp.sender == deal.value.borrower:
            self.transfer_tokens(f=deal.value.borrower, t=deal.value.creditor, v=(deal.value.amount+deal.value.reward), token_address=deal.value.token_address)
            sp.if deal.value.deposit > sp.mutez(0):
                sp.send(deal.value.borrower, deal.value.deposit)
                self.data.deposits -= deal.value.deposit
        sp.else:
            sp.verify(deal.value.exp < sp.now, message = Error.ACCESS_DENIED)
            sp.if deal.value.deposit > sp.mutez(0):
                sp.send(deal.value.creditor, deal.value.deposit)
                self.data.deposits -= deal.value.deposit
        del self.data.deals[params.id]


    # Help function to transfer tokens.
    # @f – source address
    # @t – destination address
    # @v – amount of tokens
    # @token_address – token smart-contract address
    #
    def transfer_tokens(self, f, t, v, token_address):
        param_type = sp.TRecord(from_ = sp.TAddress, to_ = sp.TAddress, value = sp.TNat).layout(("from_ as from", ("to_ as to", "value")))
        param_values = sp.record(from_ = f, to_ = t, value = v)
        sp.transfer(param_values, sp.mutez(0), sp.contract(param_type, token_address, entry_point="transfer").open_some())



#########################################################################################################
# Tests
@sp.add_test(name = "Opus")
def test():
    creator = sp.address("tz1fE6hEiRFa9ZHJeZrccNKsGW7jdxfe9vcv")
    DAY = 86400
    admin = sp.test_account("Admin")
    userA = sp.test_account("UserA")
    userB = sp.test_account("UserB")
    userC = sp.test_account("UserC")
    scenario = sp.test_scenario()
    scenario.h1("Opus tests")
    c1 = Opus(creator)
    INITIAL_BALANCE = sp.tez(1000)
    c1.set_initial_balance(INITIAL_BALANCE)
    scenario += c1


    scenario.h1("Admins")
    scenario.h2("add_admin()")
    c1.add_admin(address=userA.address).run(sender = creator, amount=sp.mutez(1), valid = False)
    c1.add_admin(address=userA.address).run(sender = userA, valid = False)
    c1.add_admin(address=admin.address).run(sender = creator)
    c1.add_admin(address=admin.address).run(sender = creator, valid = False)
    c1.add_admin(address=userA.address).run(sender = admin)
    scenario.h2("remove_admin()")
    c1.remove_admin(address=userA.address).run(sender = admin, amount=sp.mutez(1), valid = False)
    c1.remove_admin(address=admin.address).run(sender = userB, valid = False)
    c1.remove_admin(address=creator).run(sender = admin, valid = False)
    c1.remove_admin(address=userA.address).run(sender = admin)
    c1.remove_admin(address=userA.address).run(sender = admin, valid = False)


    scenario.h1("Delegate")
    scenario.h2("delegate()")
    keyHash = sp.key_hash("tz1fwnfJNgiDACshK9avfRfFbMaXrs3ghoJa")
    voting_powers = {keyHash : 0}
    c1.delegate(baker=sp.some(keyHash)).run(sender = admin, voting_powers = voting_powers, amount=sp.mutez(1), valid = False)
    c1.delegate(baker=sp.some(keyHash)).run(sender = userB, voting_powers = voting_powers, valid = False)
    c1.delegate(baker=sp.some(keyHash)).run(sender = admin, voting_powers = voting_powers)
    c1.delegate(baker=sp.some(keyHash)).run(sender = admin, voting_powers = voting_powers, valid = False)
    scenario.verify_equal(c1.baker, sp.some(keyHash))
    c1.delegate(baker=sp.none).run(sender = admin)


    scenario.h1("Tokens")
    tokenBTC = sp.record(name="sBTC", address=sp.address("tz1oBTCoMEtsXm3QxA7FmMU2Qh7xzsuGXVbc"))
    tokenETH = sp.record(name="sETH", address=sp.address("tz1oETHo1otsXm3QxA7FmMU2Qh7xzsuGXVbc"))
    tokenXPR = sp.record(name="sXRP", address=sp.address("tz1oXRPoMEtsXm3QxA7FmMU2Qh7xzsuGXVbc"))
    scenario.h2("add_token()")
    c1.add_token(tokenBTC).run(sender = creator, amount=sp.mutez(1), valid = False)
    c1.add_token(tokenBTC).run(sender = creator)
    c1.add_token(tokenETH).run(sender = userA, valid = False)
    c1.add_token(name=tokenETH.name, address=sp.address("tz1oETHo2otsXm3QxA7FmMU2Qh7xzsuGXVbc")).run(sender = creator)
    c1.add_token(tokenETH).run(sender = admin)
    c1.add_token(tokenXPR).run(sender = admin)
    scenario.h2("remove_token()")
    c1.remove_token(name="sBTC").run(sender = creator, amount=sp.mutez(1), valid = False)
    c1.remove_token(name="sBTC").run(sender = userA, valid = False)
    c1.remove_token(name="yyyy").run(sender = creator, valid = False)
    c1.remove_token(name="sXRP").run(sender = creator)


    scenario.h1("Fee")
    scenario.h2("set_fee()")
    c1.set_fee(fee=0).run(sender = creator, amount=sp.mutez(1), valid = False)
    c1.set_fee(fee=0).run(sender = userA, valid = False)
    c1.set_fee(fee=100).run(sender = creator, valid = False)
    c1.set_fee(fee=10000).run(sender = creator, valid = False)
    c1.set_fee(fee=0).run(sender = creator)
    c1.set_fee(fee=100).run(sender = admin)


    scenario.h1("Min Deposit")
    scenario.h2("set_min_deposit()")
    c1.set_min_deposit(min_deposit=sp.mutez(100)).run(sender = creator, amount=sp.mutez(1), valid = False)
    c1.set_min_deposit(min_deposit=sp.mutez(0)).run(sender = userA, valid = False)
    c1.set_min_deposit(min_deposit=sp.mutez(1_000_000)).run(sender = creator, valid = False)
    c1.set_min_deposit(min_deposit=sp.mutez(0)).run(sender = admin)
    c1.set_min_deposit(min_deposit=sp.mutez(1_000_000)).run(sender = creator)


    scenario.h1("Time")
    scenario.h2("set_time()")
    c1.set_time(sp.record(min=1*DAY, max=366*DAY)).run(sender = creator, amount=sp.mutez(1), valid = False)
    c1.set_time(sp.record(min=3*DAY, max=60*DAY)).run(sender = userA, valid = False)
    c1.set_time(sp.record(min=0*DAY, max=366*DAY)).run(sender = creator, valid = False)
    c1.set_time(sp.record(min=180*DAY, max=7*DAY)).run(sender = creator, valid = False)
    c1.set_time(sp.record(min=1*DAY, max=366*DAY)).run(sender = admin)
    c1.set_time(sp.record(min=1*DAY, max=366*DAY)).run(sender = creator, valid = False)


    scenario.h1("Loans")
    scenario.h2("add_loan()")
    c1.add_loan(amount=10_000, token="abcd", token_address=tokenETH.address, time=7*DAY, reward=1000,
        deposit=sp.mutez(1_500_000_00), validity=sp.some(sp.timestamp_from_utc(2022, 5, 14, 0, 0, 0))
        ).run(sender=userA, amount=sp.mutez(1_500_000_00 + 28767), now=sp.timestamp_from_utc(2022, 5, 1, 0, 0, 0), valid = False)
    c1.add_loan(amount=10_000, token=tokenETH.name, token_address=sp.address("tz1fwnfJNgiDACshK9avfRfFbMaXrs3ghoJa"), time=7*DAY, reward=1000,
        deposit=sp.mutez(1_500_000_00), validity=sp.some(sp.timestamp_from_utc(2022, 5, 14, 0, 0, 0))
        ).run(sender=userA, amount=sp.mutez(1_500_000_00 + 28767), now=sp.timestamp_from_utc(2022, 5, 1, 0, 0, 0), valid = False)
    c1.add_loan(amount=0, token=tokenETH.name, token_address=tokenETH.address, time=7*DAY, reward=1000,
        deposit=sp.mutez(1_500_000_00), validity=sp.some(sp.timestamp_from_utc(2022, 5, 14, 0, 0, 0))
        ).run(sender=userA, amount=sp.mutez(1_500_000_00 + 28767), now=sp.timestamp_from_utc(2022, 5, 1, 0, 0, 0), valid = False)
    c1.add_loan(amount=10_000, token=tokenETH.name, token_address=tokenETH.address, time=7*DAY, reward=1000,
        deposit=sp.mutez(1), validity=sp.some(sp.timestamp_from_utc(2022, 5, 14, 0, 0, 0))
        ).run(sender=userA, amount=sp.mutez(1_500_000_00 + 28767), now=sp.timestamp_from_utc(2022, 5, 1, 0, 0, 0), valid = False)
    c1.add_loan(amount=10_000, token=tokenETH.name, token_address=tokenETH.address, time=1, reward=1000,
        deposit=sp.mutez(1_500_000_00), validity=sp.some(sp.timestamp_from_utc(2022, 5, 14, 0, 0, 0))
        ).run(sender=userA, amount=sp.mutez(1_500_000_00 + 28767), now=sp.timestamp_from_utc(2022, 5, 1, 0, 0, 0), valid = False)
    c1.add_loan(amount=10_000, token=tokenETH.name, token_address=tokenETH.address, time=456*DAY, reward=1000,
        deposit=sp.mutez(1_500_000_00), validity=sp.some(sp.timestamp_from_utc(2022, 5, 14, 0, 0, 0))
        ).run(sender=userA, amount=sp.mutez(1_500_000_00 + 28767), now=sp.timestamp_from_utc(2022, 5, 1, 0, 0, 0), valid = False)
    c1.add_loan(amount=10_000, token=tokenETH.name, token_address=tokenETH.address, time=7*DAY, reward=1000,
        deposit=sp.mutez(1_500_000_00), validity=sp.some(sp.timestamp_from_utc(2022, 5, 1, 0, 0, 0))
        ).run(sender=userA, amount=sp.mutez(1_500_000_00 + 28767), now=sp.timestamp_from_utc(2022, 5, 1, 0, 0, 0), valid = False)
    c1.add_loan(amount=10_000, token=tokenETH.name, token_address=tokenETH.address, time=7*DAY, reward=1000,
        deposit=sp.mutez(1_500_000_00), validity=sp.some(sp.timestamp_from_utc(2022, 5, 14, 0, 0, 0))
        ).run(sender=userA, amount=sp.mutez(1_500_000_00), now=sp.timestamp_from_utc(2022, 5, 1, 0, 0, 0), valid = False)
    c1.add_loan(amount=10_000, token=tokenETH.name, token_address=tokenETH.address, time=7*DAY, reward=1000, deposit=sp.mutez(1_500_000_00),
        validity=sp.some(sp.timestamp_from_utc(2022, 5, 14, 0, 0, 0))
        ).run(sender=userA, amount=sp.mutez(1_500_000_00 + 28767), now=sp.timestamp_from_utc(2022, 5, 1, 0, 0, 0))
    c1.add_loan(amount=20_000, token=tokenBTC.name, token_address=tokenBTC.address, time=14*DAY, reward=200, deposit=sp.mutez(200_000_000),
        validity=sp.none
        ).run(sender=userB, amount=sp.mutez(200_000_000 + 76712), now=sp.timestamp_from_utc(2022, 5, 2, 0, 0, 0))
    c1.add_loan(amount=10_000, token=tokenETH.name, token_address=tokenETH.address, time=7*DAY, reward=100, deposit=sp.mutez(1_000_000),
        validity=sp.some(sp.timestamp_from_utc(2022, 5, 3, 0, 0, 0))
        ).run(sender=userA, amount=sp.mutez(1_000_000 + 191), now=sp.timestamp_from_utc(2022, 5, 1, 0, 0, 0))
    c1.add_loan(amount=10_000, token=tokenETH.name, token_address=tokenETH.address, time=7*DAY, reward=1000, deposit=sp.mutez(1_500_000_00),
        validity=sp.some(sp.timestamp_from_utc(2022, 5, 14, 0, 0, 0))
        ).run(sender=userA, amount=sp.mutez(1_500_000_00 + 28767), now=sp.timestamp_from_utc(2022, 5, 1, 0, 0, 0))
    c1.add_loan(amount=10_000, token=tokenETH.name, token_address=tokenETH.address, time=7*DAY, reward=1000, deposit=sp.mutez(1_000_000),
        validity=sp.some(sp.timestamp_from_utc(2022, 5, 3, 0, 0, 0))
        ).run(sender=userA, amount=sp.mutez(1_000_000 + 191), now=sp.timestamp_from_utc(2022, 5, 1, 0, 0, 0))
    c1.add_loan(amount=20_000, token="eth", token_address=tokenETH.address, time=14*DAY, reward=200, deposit=sp.mutez(200_000_000),
        validity=sp.none
        ).run(sender=userB, amount=sp.mutez(200_000_000 + 76712), now=sp.timestamp_from_utc(2022, 5, 2, 0, 0, 0), valid=False)
    c1.add_loan(amount=20_000, token=tokenBTC.name, token_address=tokenETH.address, time=14*DAY, reward=200, deposit=sp.mutez(200_000_000),
        validity=sp.none
        ).run(sender=userB, amount=sp.mutez(200_000_000 + 76712), now=sp.timestamp_from_utc(2022, 5, 2, 0, 0, 0), valid=False)
    scenario.h2("cancel_loan()")
    c1.cancel_loan(id=1).run(sender = userA, amount=sp.mutez(1), valid = False)
    c1.cancel_loan(id=123).run(sender = userA, valid = False)
    c1.cancel_loan(id=3).run(sender = userB, valid = False)
    c1.cancel_loan(id=1).run(sender = userA)
    c1.cancel_loan(id=3).run(sender = admin)


    scenario.h1("Deals")
    scenario.h2("make_deal()")
    c1.make_deal(id=1).run(sender=userB, valid = False)
    c1.make_deal(id=4).run(sender=userA, valid = False)
    c1.make_deal(id=4).run(sender=userB, now=sp.timestamp_from_utc(2022, 5, 15, 0, 0, 0), valid = False)
    c1.make_deal(id=4).run(sender=userB, now=sp.timestamp_from_utc(2022, 5, 10, 0, 0, 0), amount=sp.mutez(1), valid = False)
    c1.make_deal(id=4).run(sender=userB, now=sp.timestamp_from_utc(2022, 5, 10, 0, 0, 0))
    c1.make_deal(id=5).run(sender=userB, now=sp.timestamp_from_utc(2022, 5, 1, 0, 0, 0))
    scenario.h2("close_deal()")
    c1.close_deal(id=0).run(sender=userA, now=sp.timestamp_from_utc(2022, 5, 11, 0, 0, 0), valid = False)
    c1.close_deal(id=1).run(sender=userC, now=sp.timestamp_from_utc(2022, 5, 11, 0, 0, 0), valid = False)
    c1.close_deal(id=1).run(sender=userB, now=sp.timestamp_from_utc(2022, 5, 11, 0, 0, 0), valid = False)
    c1.close_deal(id=1).run(sender=admin, now=sp.timestamp_from_utc(2022, 5, 11, 0, 0, 0), valid = False)
    c1.close_deal(id=1).run(sender=userA, now=sp.timestamp_from_utc(2022, 5, 14, 0, 0, 0), amount=sp.mutez(1), valid = False)
    c1.close_deal(id=1).run(sender=userA, now=sp.timestamp_from_utc(2022, 5, 14, 0, 0, 0))
    c1.close_deal(id=2).run(sender=userB, now=sp.timestamp_from_utc(2022, 5, 9, 0, 0, 0))


    scenario.h1("Pause")
    scenario.h2("pause()")
    c1.pause(pause=True).run(sender = admin, amount=sp.mutez(1), valid = False)
    c1.pause(pause=False).run(sender = userA, valid = False)
    c1.pause(pause=False).run(sender = admin, valid = False)
    c1.pause(pause=True).run(sender = admin)
    # Creating new loan request is not possible
    c1.add_loan(amount=10_000, token=tokenETH.name, token_address=tokenETH.address, time=7*DAY, reward=100, deposit=sp.mutez(1_000_000),
        validity=sp.some(sp.timestamp_from_utc(2022, 5, 3, 0, 0, 0))
        ).run(sender=userA, amount=sp.mutez(1_000_000 + 191), now=sp.timestamp_from_utc(2022, 5, 1, 0, 0, 0), valid = False)
    # Making deal is not possible
    c1.make_deal(id=2).run(sender=userC, valid = False)


    scenario.h1("Withdraw")
    scenario.h2("withdraw()")
    c1.withdraw(address=admin.address, amount=sp.mutez(1)).run(sender = userA, valid = False)
    c1.withdraw(address=admin.address, amount=sp.mutez(0)).run(sender = creator, valid = False)
    c1.withdraw(address=admin.address, amount=sp.tez(1000000)).run(sender = admin, valid = False)
    c1.withdraw(address=admin.address, amount=INITIAL_BALANCE).run(sender = admin)
    scenario.verify(c1.balance >= c1.data.deposits)


sp.add_compilation_target("opus", Opus("tz1fE6hEiRFa9ZHJeZrccNKsGW7jdxfe9vcv"))
