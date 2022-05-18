<h1 align="center">
  <a href="https://github.com/dec0dOS/amazing-github-template">
    <img src="https://opusdei.money/img/logo.svg" alt="Logo" width="85" height="85">
  </a>
</h1>



<div align="center">
<br />

[![license](https://img.shields.io/github/license/dec0dOS/amazing-github-template.svg?style=flat-square)](LICENSE)
![version](https://img.shields.io/badge/build%20version-0.7-orange)

</div>



# OPD 0.7
This project is intended to provide an easy and efficient way to lend and/or borrow tokens and XTZ on [Tezos blockchain](https://tezos.com). This version allows users to use only XTZ as collateral 

The current implementation supports FA1.2


---


The functionality of this service consists of several simple steps:


1. `Log In` Enter the system with your wallet. 
2. `Borrow.` Create a borrow request by providing the necessary information, like the choice of a token you want to borrow ( = the reward token), the number of tokens to borrow, the number of tokens as collateral and the reward, time (loan term). There is an optional field *"Deadline"* for liquidation of the request if it wasn't accepted by a creditor:
- **Loan.** Select a token from the select list.
- **Reward.** Paid in selected token (Loan).
- **Colateral.** Tezos XTZ as a default in this version.
- **Loan Term.** For how long will be the loan taken.
- **Deadline.** Optional field. Loan request termination date. 
3. `Lend.` View borrowing requests from other users and lend requested tokens.
4. `Deals.` View and repay existing deals - both borrowings and lendings


---

## License
This project is licensed under the MIT license.

---

## No Further Development. 
The development team behind the project (the OPD team) represents and warrants that it has terminated all development efforts and activities related to this version of the protocol (0.7). The OPD team further warrants that it will not undertake additional development work related to the existing technology, existing software, improvements, new technology or new software in this project. 
Next versions of the protocol will be published as new projects or repositories.
