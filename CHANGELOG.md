# Changelog

## [Unreleased]

## [v0.4.0] - 2018-02-28

### Bug fixes
- :bug: fix(backend): Miner temperatures returned as 'NULL'. Closes #74

### New Features
- :up: update(create_db): Add support for Antminer R4. Closes #66
- :up: update(create_db): Add support for V9
- :up: update(requirements,app): Add Flask-Migrate
- :up: update(requirements,app): Add manager.py script

### Added
- :up: update(css): Add generic default font-family
- :up: update(donations): Add Ethereum widget

### Changed
- :shirt: refactor(css): Add grid layout
- :up: update(css): Change body width to 90%
- :up: update(debug): Update debug flash messages
- :shirt: refactor(code): Move helper functions to the lib folder
- :heavy_plus_sign: :shirt: refactor(js): Move scripts to separate files
- :shirt: refactor(static): Organize static files
- :shirt: refactor(templates): Split main template into layout and base
- :pencil: docs(run): Update run command

## [v0.3.0] - 2018-01-28
### Bug fixes
- :bug: fix(table): Fix remove icon not showing
- :bug: fix(table): Fix remove icon not showing in inactive miners

### New Features
- :zap: improvement: Add conversion of hashrate unit
- :zap: improvement(update_unit_and_value): Add support for Peta and Exa Hash
- :zap: improvement(pycgminer): Add support for Python3. Closes #10
- :up: update(create_db): Add support for T9. Closes #25
- :up: update(create_db): Add support for A3. Closes #59
- :up: update(create_db): Add support for L3

### Added
- :lipstick: update: Add remove miner icon
- :star: new(table): Add Worker column
- :heavy_plus_sign: Add update_db script
- :pencil: docs(donations): Add ETH address

### Changed
- :lipstick: update: Remove JSON Info column
- :shirt: refactor(views): Move json views to a separate file
- :up: update(create_db): Add error handling. Print messages Fix #34
- :heavy_plus_sign: :shirt: refactor(css): Separate most css from html
- :pencil: docs(readme): Update README
Updated supported miner models, requirements and installation instructions. Added update instructions

## [v0.2.0] - 2017-11-10
### Bug fixes
- :pencil: docs(screenshot): Showing Wrong version. Closes #13
- :up: update(fieldset): Fix typo in fieldset name. Closes #18
- :wrench: config(hashrate): Hash rate not showing up correctly. Closes #22

### New Features
- :star: new(autorefresh): Add auto-refresh feature. Closes #14
- :star: new(table): Add new cell with chip condition '-'. Closes #16

### Added
- :pencil: docs(donations): Add donations
- :pencil: docs(requirements): Add requirements
- :pencil: docs(referral): Add referral
- :pencil: docs(badges): Add twitter badge

### Changed
- :pencil: docs(installation): Update installation command

## [v0.1.1] - 2017-10-28
### Bug fixes
- :pencil: docs(changelog): Fix typos in CHANGELOG. Closes #11
- :bug: fix(table): Rename <th>HW Errors</th>. Closes #12

## [v0.1.0] - 2017-10-25
### New Features
- :star2: new: Add miner's HW Error Rate
- :star: new: Add miner's uptime

## [v0.0.3] - 2017-10-24
### Bug fixes
- :zap: improvement(table): Fixed #2, Sort temperatures and fan speed by board and fan respectively
- :bug: fix: Fixed #4, Total hashing speed is displayed many times
- :bug: fix: Fixed #5, Remarks not displayed on active miners
- :wrench: config(table): Fixed #6, Sort miners by IP
- :zap: improvement: Sort models in total hashrate panel
- :wrench: config: Sort dropdown items by model type in add form

### New Features
- :heavy_plus_sign: Added CHANGELOG.md

## [v0.0.2] - 2017-10-08
### Bug fixes
- :wrench: config(log): Updated logging Formatter
- :wrench: config(views): Updated index url from /miners to /
- :bug: Fixed bug showing 'No errors found.' when there are inactive miners

### New Features
- :star: Added individual miner hashrate
- :star2: Added card to display total hashrate grouped by Model

## v0.0.1 - 2017-10-05
### Features
- :star2: Add as many miners as you want
- :star: Support for Antminers S7, S9, L3+ and D3
- :star: Check their temperatures, fan speed, chip condition
- :star: Get in-app notifications about miner errors (needs refresh)
- :star: Log errors to file

[Unreleased]: https://github.com/anselal/antminer-monitor/compare/v0.4.0...HEAD
[v0.4.0]: https://github.com/anselal/antminer-monitor/compare/v0.3.0...v0.4.0
[v0.3.0]: https://github.com/anselal/antminer-monitor/compare/v0.2.0...v0.3.0
[v0.2.0]: https://github.com/anselal/antminer-monitor/compare/v0.1.1...v0.2.0
[v0.1.1]: https://github.com/anselal/antminer-monitor/compare/v0.1.0...v0.1.1
[v0.1.0]: https://github.com/anselal/antminer-monitor/compare/v0.0.3...v0.1.0
[v0.0.3]: https://github.com/anselal/antminer-monitor/compare/v0.0.2...v0.0.3
[v0.0.2]: https://github.com/anselal/antminer-monitor/compare/v0.0.1...v0.0.2