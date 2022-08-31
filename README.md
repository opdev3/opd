<h1 align="center">
  <a href="https://opusdei.money/">
    <img src="https://opusdei.money/img/logo.svg" alt="Logo" width="85" height="85">
  </a>
</h1>



<div align="center">
<br />

[![license](https://img.shields.io/github/license/dec0dOS/amazing-github-template.svg?style=flat-square)](LICENSE)
![version](https://img.shields.io/badge/build%20version-0.71-orange)

</div>



# Opus Dei Money Protocol
Opus Dei Money Protocol (OPD) is a fully decentralised and Open Source peer-to-peer (P2P) service for an easy and efficient way to lend and/or borrow tokens and XTZ built on top of the [Tezos blockchain](https://tezos.com). 

OPD allows lenders and borrowers to create a P2P lending agreements securely and transparently using Blockchain and Smart Contracts. P2P crypto-to-crypto lending removes the need for banks to be the only available option for borrowing. By placing a loan request on Opus Dei Money Protocol, lenders can fund loan requests by competing to provide the most competitive interest rate. OPD provides transparent and trustless decentralised solutions to avoid loss of capital, making a true global lending market available.


## What is Peer-to-Peer crypto lending?

Peer-to-peer or P2P crypto lending is a process that lets a user lend cryptocurrencies directly to a borrower who wants to take out a crypto-backed loan.

P2P crypto lending minimizes the role of the third party (even the platform itself) in the lending and borrowing processes. Rather than funding the loan itself, with the use of P2P platforms, users can:

* Set rates and terms of the loan.
* Ease money transfers between lender and borrower.
* Ask the borrower to pay down or add more collateral to their loan if the value drops significantly.
* Collaborate with a custodian to hold the crypto assets while the loan is in repayment.
* Offer some kind of insurance to protect the collateral in repayment.

On a P2P platform, lenders choose the rates, terms and amount they want to fund. That allows for more control over the investment than parking that money in an account that offers a flat APY.

## Benefits of Peer-to-Peer lending

* Increased scalability. There are millions of people all over the world with no access to a bank account. At the same time, traditional financial institutions have dramatically lost the trust of consumers. 
* Faster and more efficient process. The automatic process of matching that takes place makes the whole task of lending very easy and fast. One doesn’t need to wait much as participants from all over the world are present on the platform, increasing the chances of investment and loan. Also, transactions done on the blockchain platform are really quick, especially when compared to traditional financial institutions.
* Reduced cost: Since the need for a middleman is eradicated, their charges also go away. Also, one doesn’t need to pay sky-rocketing interest rates as they are already fixed by smart contracts based on the risk profile of the borrower.
* Loan tokenization: The transformation of assets into units that store value is called loan tokenization. It is a pertinent advantage offered by blockchain platforms. Participants can exchange anything, in any currency on a blockchain platform- transparently and securely.
* Identity protection: Blockchain platforms don’t require you to enter bank details or credit card numbers, protecting your fiat money. Digital money doesn’t ask for details other than the amount of the transaction.
* Trustless. There is no need to trust the counterparty. When the borrower places the loan request on OPD, the counterparty, OPD or any other party cannot manipulate, stop and prevent the loan request once the loan is deployed. Instead of the need to trust the counterparty, decentralisation removes the necessity to trust your provider and your counterparty.

Peer-to-peer lending platforms presage a more inclusive and accessible financial services system.

# OPD 0.71
This version allows users to use only XTZ as collateral and supports FA1.2 standard tokens



---

The functionality of this version consists of several simple steps:


1. `Log In` Enter the system with your wallet. 
2. `Borrow.` Create a borrow request by providing the necessary information, like the choice of a token you want to borrow ( = the reward token), the number of tokens to borrow, the number of tokens as collateral and the reward, time (loan term). There is an optional field *"Deadline"* for liquidation of the request if it wasn't accepted by a creditor:
- **Loan.** Select a token from the select list.
- **Reward.** Paid in selected token (Loan).
- **Colateral.** Tezos XTZ as a default in this version.
- **Loan Term.** For how long will be the loan taken.
- **Deadline.** Optional field. Loan request termination date. 
3. `Lend.` View borrowing requests from other users and lend requested tokens.
4. `Deals.` View and repay existing deals - both borrowings and lendings

# How it works for lenders

* Enter the service with your Tezos wallet by clicking the Enter App button.
* Choose your preferred wallet from the list.
* Approve the permission request from the wallet. 
* Visit the **Lend** section from the platform’s dashboard for loans to be funded. Select a loan to fund. Check if the loan request reward and collateral are good for you.
* Make sure the necessary crypto asset is in the wallet.
* Click on the **Supply** button from the pop-up you see after clicking on a loan row.
* Approve the permission request from the wallet.
* Collect the reward together with the asset when the loan is returned. If the borrower fails to repay the loan, you can seize the borrower’s collateral to make up for your losses.
* **Important!** If the borrower fails to repay the loan, the system will not send you the collateral. You will have to collect the collateral manually! 

# How it works for borrowers


* Enter the service with your Tezos wallet by clicking the Enter App button.
* Choose your preferred wallet from the list.
* Approve the permission request from the wallet. 
* Visit the **Borrow** section from the platform’s dashboard to see your active loan requests.
* **Create a new loan request** by clicking the **+New Request** button.
* **The Borrow Pop-up**:
 1. `Loan` Choose an asset to borrow from the drop-down list.
 2. `Enter Amount` Enter the number of tokens you want to borrow.
 3. `Reward` Reward token type is chosen automatically with the Loan. Set the reward amount manually. 
    - **The reward is given to a lender in recognition of their provided liquidity. The higher the reward, the more attractive the request. The Greater the Effort, the Sweeter the Reward**
 4. `Collateral` Set the amount of XTZ a lender will get if the loan is not paid in time. Same as the reward affects the attractiveness of your request.
 5. `Loan term` Choose the time of your request - how long you want to keep the asset. You can pay it back before the time runs out. If you don't pay it in time, the lender will seize your collateral.
 6. `Deadline (optional)` You can set the timing for that request to be active until someone fills it up.
* Approve the new loan request from the wallet.
* You will see the loan request from the **Borrow** section. A lender will see it from the **Lend** section as a loan to supply

---

## Glossary
| Term | Description |
| --- | --- |
| APY | Annual Percentage Yield. The rate to earn on an account over a year and it includes compound interest. |
| FA1.2 | FA1.2 refers to an [ERC20](https://eips.ethereum.org/EIPS/eip-20)-like fungible token standard (TZIP-7) for Tezos. At its core, FA1.2 contains a ledger which maps identities to token balances, providing a standard API for token transfer operations, as well as providing approval to external contracts (e.g. an auction) or accounts to transfer a user's tokens. The FA1.2 specification is described in details in [TZIP-7](https://gitlab.com/tezos/tzip/-/blob/master/proposals/tzip-7/tzip-7.md). |
| P2P | Peer-to-Peer. Relating to, using, or being a network by which computers operated by individuals can share information and resources directly without relying on a dedicated central server. |
| P2P Lending | Peer-to-peer lending networks consist of two or more computers that interact to communicate, share data, and provide lending services without the need for a central server. The P2P lending networks of yesterday are beginning to integrate with blockchain-based smart contracts, contributing to the evolution of decentralized finance (DeFi). The resulting networks facilitate trustless transactions that lower costs and save time by removing intermediaries. Peer-to-peer lending has become a significant subset of the DeFi ecosystem, and its growth is accelerating. |
| Smart Contract | A self-executing contract with the terms of the agreement between buyer and seller being directly written into lines of code. The code and the agreements contained therein exist across a distributed, decentralized blockchain network. |
| XTZ | The native cryptocurrency for the Tezos blockchain. Also known as Tez or  tezzie. |

---

## License
This project is licensed under the MIT license.

---

## No Further Development
The development team behind the project (the OPD team) represents and warrants that it has terminated all development efforts and activities related to this version of the protocol (0.71). The OPD team further warrants that it will not undertake additional development work related to the existing technology, existing software, improvements, new technology or new software in this project. 
Next versions of the protocol will be published as new projects or repositories.
