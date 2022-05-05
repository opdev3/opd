import smartpy as sp

class Error:
    ACCESS_DENIED       = "OD_ACCESS_DENIED"
    ILLEGAL_ARGUMENT    = "OD_ILLEGAL_ARGUMENT"
    PAUSED              = "OD_PAUSED"


class Opus(sp.Contract):
    def __init__(self, creator):
        self.creator = creator
        self.init(
            pause = False,
            baker = sp.none,
            admins = sp.set([creator]),
            tokens = sp.map(tkey = sp.TString, tvalue = sp.TAddress),
            time = sp.record(min = sp.int(7 * 86400), max = sp.int(180 * 86400)),
            fee = sp.nat(100),
            mindeposit = sp.tez(1),
            nloan = sp.nat(0),
            ndeal = sp.nat(0),
            loans = {},
            deals = {},
            deposits = sp.mutez(0)
        )


    @sp.entry_point
    def default(self):
        pass


    @sp.entry_point
    def addAdmin(self, params):
        sp.set_type(params.address, sp.TAddress)
        sp.verify(self.data.admins.contains(sp.sender), message = Error.ACCESS_DENIED)
        sp.verify(~self.data.admins.contains(params.address), message = Error.ILLEGAL_ARGUMENT)
        self.data.admins.add(params.address)


    @sp.entry_point
    def removeAdmin(self, params):
        sp.set_type(params.address, sp.TAddress)
        sp.verify(self.data.admins.contains(sp.sender), message = Error.ACCESS_DENIED)
        sp.verify(self.creator != params.address, message = Error.ILLEGAL_ARGUMENT)
        sp.verify(self.data.admins.contains(params.address), message = Error.ILLEGAL_ARGUMENT)
        self.data.admins.remove(params.address)


    @sp.entry_point
    def setPause(self, params):
        sp.set_type(params.pause, sp.TBool)
        sp.verify(self.data.admins.contains(sp.sender), message = Error.ACCESS_DENIED)
        sp.verify(self.data.pause != params.pause, message = Error.ILLEGAL_ARGUMENT)
        self.data.pause = params.pause


    @sp.entry_point
    def delegate(self, params):
        sp.set_type(params.baker, sp.TOption(sp.TKeyHash))
        sp.verify(self.data.admins.contains(sp.sender), message = Error.ACCESS_DENIED)
        sp.verify(self.data.baker != params.baker, message = Error.ILLEGAL_ARGUMENT)
        self.data.baker = params.baker
        sp.set_delegate(params.baker)


    @sp.entry_point
    def addToken(self, params):
        sp.set_type(params.name, sp.TString)
        sp.set_type(params.address, sp.TAddress)
        sp.verify(self.data.admins.contains(sp.sender), message = Error.ACCESS_DENIED)
        self.data.tokens[params.name] = params.address


    @sp.entry_point
    def removeToken(self, params):
        sp.set_type(params.name, sp.TString)
        sp.verify(self.data.admins.contains(sp.sender), message = Error.ACCESS_DENIED)
        sp.verify(self.data.tokens.contains(params.name), message = Error.ILLEGAL_ARGUMENT)
        del self.data.tokens[params.name]


    @sp.entry_point
    def setFee(self, params):
        sp.set_type(params.fee, sp.TNat)
        sp.verify(self.data.admins.contains(sp.sender), message = Error.ACCESS_DENIED)
        sp.verify(self.data.fee != params.fee, message = Error.ILLEGAL_ARGUMENT)
        sp.verify((params.fee >= 0) & (params.fee < 10000), message = Error.ILLEGAL_ARGUMENT)
        self.data.fee = params.fee

    @sp.entry_point
    def setMinDeposit(self, params):
        sp.set_type(params.mindeposit, sp.TMutez)
        sp.verify(self.data.admins.contains(sp.sender), message = Error.ACCESS_DENIED)
        sp.verify(self.data.mindeposit != params.mindeposit, message = Error.ILLEGAL_ARGUMENT)
        sp.verify(params.mindeposit >= sp.mutez(0), message = Error.ILLEGAL_ARGUMENT)
        self.data.mindeposit = params.mindeposit


    @sp.entry_point
    def setTime(self, params):
        sp.set_type(params, sp.TRecord(min = sp.TInt, max = sp.TInt))
        sp.verify(self.data.admins.contains(sp.sender), message = Error.ACCESS_DENIED)
        sp.verify(self.data.time != params, message = Error.ILLEGAL_ARGUMENT)
        sp.verify((params.min > 0) & (params.min <= params.max), message = Error.ILLEGAL_ARGUMENT)
        self.data.time = params


    @sp.entry_point
    def addLoan(self, params):
        sp.verify(~self.data.pause, message = Error.PAUSED)
        sp.set_type(params.amount, sp.TNat)
        sp.set_type(params.reward, sp.TNat)
        sp.set_type(params.deposit, sp.TMutez)
        sp.set_type(params.validity, sp.TOption(sp.TTimestamp))
        sp.verify(params.amount > 0, message = Error.ILLEGAL_ARGUMENT)
        sp.verify(params.reward >= 0, message = Error.ILLEGAL_ARGUMENT)
        sp.verify(self.data.tokens.contains(params.token), message = Error.ILLEGAL_ARGUMENT)
        sp.verify(self.data.tokens[params.token] == params.tokenaddress, message = Error.ILLEGAL_ARGUMENT)
        sp.verify((params.time >= self.data.time.min) & (params.time <= self.data.time.max), message = Error.ILLEGAL_ARGUMENT)
        sp.verify(params.deposit >= self.data.mindeposit, message = Error.ILLEGAL_ARGUMENT)
        f = sp.local("f", sp.utils.nat_to_mutez(sp.utils.mutez_to_nat(params.deposit) * sp.as_nat(params.time) * self.data.fee // (3600 * 24 * 365 * 100 * 100)))
        sp.verify((params.deposit + f.value) == sp.amount, message = Error.ILLEGAL_ARGUMENT)
        sp.verify((params.validity == sp.none) | (params.validity > sp.some(sp.now)), message = Error.ILLEGAL_ARGUMENT)
        loan = sp.record(
            ts = sp.now,
            borrower = sp.sender,
            validity = params.validity,
            amount = params.amount,
            token = params.token,
            tokenaddress = self.data.tokens[params.token],
            time = params.time,
            reward = params.reward,
            deposit = params.deposit,
            fee = f.value
        )
        self.data.nloan += 1
        self.data.loans[self.data.nloan] = loan
        self.data.deposits += sp.amount


    @sp.entry_point
    def cancelLoan(self, params):
        sp.set_type(params.id, sp.TNat)
        sp.verify(self.data.loans.contains(params.id), message = Error.ILLEGAL_ARGUMENT)
        loan = self.data.loans[params.id]
        sp.verify((sp.sender == loan.borrower) | self.data.admins.contains(sp.sender), Error.ACCESS_DENIED)
        sp.send(loan.borrower, loan.deposit + loan.fee)
        self.data.deposits -= (loan.deposit + loan.fee)
        del self.data.loans[params.id]


    @sp.entry_point
    def makeDeal(self, params):
        sp.verify(~self.data.pause, message = Error.PAUSED)
        sp.set_type(params.id, sp.TNat)
        sp.verify(self.data.loans.contains(params.id), message = Error.ILLEGAL_ARGUMENT)
        loan = self.data.loans[params.id]
        sp.verify(loan.borrower != sp.sender, Error.ILLEGAL_ARGUMENT)
        sp.verify((loan.validity == sp.none) | (loan.validity > sp.some(sp.now)), message = Error.ILLEGAL_ARGUMENT)
        deal = sp.record(
            ts = sp.now,
            borrower = loan.borrower,
            creditor = sp.sender,
            amount = loan.amount,
            token = loan.token,
            tokenaddress = loan.tokenaddress,
            exp = sp.now.add_seconds(loan.time),
            reward = loan.reward,
            deposit = loan.deposit,
        )
        self.transferTokens(f=sp.sender, t=loan.borrower, v=loan.amount, tokenaddress=loan.tokenaddress)
        self.data.ndeal += 1
        self.data.deals[self.data.ndeal] = deal
        self.data.deposits -= loan.fee
        del self.data.loans[params.id]


    @sp.entry_point
    def closeDeal(self, params):
        sp.set_type(params.id, sp.TNat)
        sp.verify(self.data.deals.contains(params.id), message = Error.ILLEGAL_ARGUMENT)
        deal = self.data.deals[params.id]
        sp.verify((sp.sender == deal.borrower) | (sp.sender == deal.creditor) | self.data.admins.contains(sp.sender), Error.ACCESS_DENIED)
        sp.if sp.sender == deal.borrower:
            self.transferTokens(f=deal.borrower, t=deal.creditor, v=(deal.amount+deal.reward), tokenaddress=deal.tokenaddress)
            sp.send(deal.borrower, deal.deposit)
            self.data.deposits -= deal.deposit
            del self.data.deals[params.id]
        sp.else:
            sp.verify(deal.exp < sp.now, message = Error.ACCESS_DENIED)
            sp.send(deal.creditor, deal.deposit)
            self.data.deposits -= deal.deposit
            del self.data.deals[params.id]


    def transferTokens(self, f, t, v, tokenaddress):
        paramType = sp.TRecord(from_ = sp.TAddress, to_ = sp.TAddress, value = sp.TNat).layout(("from_ as from", ("to_ as to", "value")))
        paramValues = sp.record(from_ = f, to_ = t, value = v)
        sp.transfer(paramValues, sp.mutez(0), sp.contract(paramType, tokenaddress, entry_point="transfer").open_some())


    @sp.entry_point
    def withdraw(self, params):
        sp.set_type(params.address, sp.TAddress)
        sp.set_type(params.amount, sp.TMutez)
        sp.verify(self.data.admins.contains(sp.sender), message = Error.ACCESS_DENIED)
        sp.verify(params.amount > sp.mutez(0), message = Error.ILLEGAL_ARGUMENT)
        sp.verify((sp.balance - self.data.deposits) >= params.amount, message = Error.ILLEGAL_ARGUMENT)
        sp.send(params.address, params.amount)



##############################################################################
# Tests
@sp.add_test(name = "Opus")
def test():
    creator = sp.address("tz1bYhHrJkaAevtpbfzZb4RBTgV9agWzsqkd")
    DAY = 86400
    admin = sp.test_account("Admin")
    userA = sp.test_account("UserA")
    userB = sp.test_account("UserB")
    userC = sp.test_account("UserC")
    scenario = sp.test_scenario()
    scenario.h1("Opus tests")
    c1 = Opus(creator)
    c1.set_initial_balance(sp.tez(1000))
    scenario += c1


    scenario.h1("Admins")
    c1.addAdmin(address=userA.address).run(sender = userA, valid = False)
    c1.addAdmin(address=admin.address).run(sender = creator)
    c1.addAdmin(address=admin.address).run(sender = creator, valid = False)
    c1.addAdmin(address=userA.address).run(sender = admin)
    c1.removeAdmin(address=admin.address).run(sender = userB, valid = False)
    c1.removeAdmin(address=creator).run(sender = admin, valid = False)
    c1.removeAdmin(address=userA.address).run(sender = admin)
    c1.removeAdmin(address=userA.address).run(sender = admin, valid = False)


    scenario.h1("Pause")
    c1.setPause(pause=True).run(sender = admin)
    c1.setPause(pause=True).run(sender = admin, valid = False)
    c1.setPause(pause=False).run(sender = userA, valid = False)
    c1.setPause(pause=False).run(sender = creator)


    scenario.h1("Delegate")
    keyHash = sp.key_hash("tz1fwnfJNgiDACshK9avfRfFbMaXrs3ghoJa")
    voting_powers = {keyHash : 0}
    c1.delegate(baker=sp.some(keyHash)).run(sender = userB, voting_powers = voting_powers, valid = False)
    c1.delegate(baker=sp.some(keyHash)).run(sender = admin, voting_powers = voting_powers)
    c1.delegate(baker=sp.some(keyHash)).run(sender = admin, voting_powers = voting_powers, valid = False)
    scenario.verify_equal(c1.baker, sp.some(keyHash))
    c1.delegate(baker=sp.none).run(sender = admin)


    scenario.h1("Tokens")
    tokenBTC = sp.record(name="sBTC", address=sp.address("tz1oBTCoMEtsXm3QxA7FmMU2Qh7xzsuGXVbc"))
    tokenETH = sp.record(name="sETH", address=sp.address("tz1oETHo1otsXm3QxA7FmMU2Qh7xzsuGXVbc"))
    tokenXPR = sp.record(name="sXRP", address=sp.address("tz1oXRPoMEtsXm3QxA7FmMU2Qh7xzsuGXVbc"))
    c1.addToken(tokenBTC).run(sender = creator)
    c1.addToken(tokenETH).run(sender = userA, valid = False)
    c1.addToken(name=tokenETH.name, address=sp.address("tz1oETHo2otsXm3QxA7FmMU2Qh7xzsuGXVbc")).run(sender = creator)
    c1.addToken(tokenETH).run(sender = creator)
    c1.addToken(tokenXPR).run(sender = creator)
    c1.removeToken(name="sBTC").run(sender = userA, valid = False)
    c1.removeToken(name="yyyy").run(sender = creator, valid = False)
    c1.removeToken(name="sXRP").run(sender = creator)


    scenario.h1("Fee")
    c1.setFee(fee=0).run(sender = creator)
    c1.setFee(fee=0).run(sender = creator, valid = False)
    c1.setFee(fee=10).run(sender = userA, valid = False)
    c1.setFee(fee=10000).run(sender = creator, valid = False)
    c1.setFee(fee=100).run(sender = creator)


    scenario.h1("Min Deposit")
    c1.setMinDeposit(mindeposit=sp.mutez(100)).run(sender = creator)
    c1.setMinDeposit(mindeposit=sp.mutez(0)).run(sender = userA, valid = False)
    c1.setMinDeposit(mindeposit=sp.mutez(100)).run(sender = creator, valid = False)


    scenario.h1("Time")
    c1.setTime(sp.record(min=3*DAY, max=60*DAY)).run(sender = userA, valid = False)
    c1.setTime(sp.record(min=0*DAY, max=366*DAY)).run(sender = creator, valid = False)
    c1.setTime(sp.record(min=180*DAY, max=7*DAY)).run(sender = creator, valid = False)
    c1.setTime(sp.record(min=1*DAY, max=366*DAY)).run(sender = creator)
    c1.setTime(sp.record(min=1*DAY, max=366*DAY)).run(sender = creator, valid = False)


    scenario.h1("Loans")
    c1.addLoan(amount=10_000, token=tokenETH.name, tokenaddress=tokenETH.address, time=7*DAY, reward=1000, deposit=sp.mutez(1_500_000_00),
        validity=sp.some(sp.timestamp_from_utc(2022, 5, 14, 0, 0, 0))
        ).run(sender=userA, amount=sp.mutez(1_500_000_00 + 28767), now=sp.timestamp_from_utc(2022, 5, 1, 0, 0, 0))
    c1.addLoan(amount=20_000, token=tokenBTC.name, tokenaddress=tokenBTC.address, time=14*DAY, reward=200, deposit=sp.mutez(200_000_000),
        validity=sp.none
        ).run(sender=userB, amount=sp.mutez(200_000_000 + 76712), now=sp.timestamp_from_utc(2022, 5, 2, 0, 0, 0))
    c1.addLoan(amount=10_000, token=tokenETH.name, tokenaddress=tokenETH.address, time=7*DAY, reward=100, deposit=sp.mutez(1_000_000),
        validity=sp.some(sp.timestamp_from_utc(2022, 5, 3, 0, 0, 0))
        ).run(sender=userA, amount=sp.mutez(1_000_000 + 191), now=sp.timestamp_from_utc(2022, 5, 1, 0, 0, 0))
    c1.cancelLoan(id=1).run(sender = userA)
    c1.cancelLoan(id=1).run(sender = userA, valid = False)
    c1.cancelLoan(id=3).run(sender = userB, valid = False)
    c1.cancelLoan(id=3).run(sender = admin)
    c1.addLoan(amount=10_000, token=tokenETH.name, tokenaddress=tokenETH.address, time=7*DAY, reward=1000, deposit=sp.mutez(1_500_000_00),
        validity=sp.some(sp.timestamp_from_utc(2022, 5, 14, 0, 0, 0))
        ).run(sender=userA, amount=sp.mutez(1_500_000_00 + 28767), now=sp.timestamp_from_utc(2022, 5, 1, 0, 0, 0))
    c1.addLoan(amount=10_000, token=tokenETH.name, tokenaddress=tokenETH.address, time=7*DAY, reward=1000, deposit=sp.mutez(1_000_000),
        validity=sp.some(sp.timestamp_from_utc(2022, 5, 3, 0, 0, 0))
        ).run(sender=userA, amount=sp.mutez(1_000_000 + 191), now=sp.timestamp_from_utc(2022, 5, 1, 0, 0, 0))
    c1.addLoan(amount=20_000, token="eth", tokenaddress=tokenETH.address, time=14*DAY, reward=200, deposit=sp.mutez(200_000_000),
        validity=sp.none
        ).run(sender=userB, amount=sp.mutez(200_000_000 + 76712), now=sp.timestamp_from_utc(2022, 5, 2, 0, 0, 0), valid=False)
    c1.addLoan(amount=20_000, token=tokenBTC.name, tokenaddress=tokenETH.address, time=14*DAY, reward=200, deposit=sp.mutez(200_000_000),
        validity=sp.none
        ).run(sender=userB, amount=sp.mutez(200_000_000 + 76712), now=sp.timestamp_from_utc(2022, 5, 2, 0, 0, 0), valid=False)


    scenario.h1("Deals")
    c1.makeDeal(id=1).run(sender=userB, valid = False)
    c1.makeDeal(id=4).run(sender=userA, valid = False)
    c1.makeDeal(id=4).run(sender=userB, now=sp.timestamp_from_utc(2022, 5, 15, 0, 0, 0), valid = False)
    c1.makeDeal(id=4).run(sender=userB, now=sp.timestamp_from_utc(2022, 5, 10, 0, 0, 0))
    c1.closeDeal(id=0).run(sender=userA, now=sp.timestamp_from_utc(2022, 5, 11, 0, 0, 0), valid = False)
    c1.closeDeal(id=1).run(sender=userC, now=sp.timestamp_from_utc(2022, 5, 11, 0, 0, 0), valid = False)
    c1.closeDeal(id=1).run(sender=userB, now=sp.timestamp_from_utc(2022, 5, 11, 0, 0, 0), valid = False)
    c1.closeDeal(id=1).run(sender=admin, now=sp.timestamp_from_utc(2022, 5, 11, 0, 0, 0), valid = False)
    c1.closeDeal(id=1).run(sender=userA, now=sp.timestamp_from_utc(2022, 5, 14, 0, 0, 0))
    c1.makeDeal(id=5).run(sender=userB, now=sp.timestamp_from_utc(2022, 5, 1, 0, 0, 0))
    c1.closeDeal(id=2).run(sender=userB, now=sp.timestamp_from_utc(2022, 5, 9, 0, 0, 0))


    scenario.h1("Withdraw")
    c1.withdraw(address=admin.address, amount=sp.mutez(1)).run(sender = userA, valid = False)
    c1.withdraw(address=admin.address, amount=sp.tez(1000000)).run(sender = creator, valid = False)
    c1.withdraw(address=admin.address, amount=sp.tez(1000)).run(sender = creator)
    c1.withdraw(address=admin.address, amount=sp.mutez(0)).run(sender = creator, valid = False)

