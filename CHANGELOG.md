# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2026-01-11

### Added
- **Advanced Database Schema** with market snapshots and exchange quotes
- **Professional Analysis Tool** (`arbitrage_pro_analysis.py`) for:
  - Exchange performance analysis
  - Hourly profitability analysis
  - Daily profitability analysis
  - Exchange pair recommendations
- **Railway Deployment** configuration files
- **PostgreSQL Support** for cloud database
- **Comprehensive Documentation** in `arbitrage/docs/`

### Changed
- Updated `arbitrage_monitor.py` to support advanced database schema
- Improved rate limiting handling
- Enhanced error handling and logging

### Fixed
- Railway Python detection issue with `runtime.txt` and `railway.json`
- Database connection handling for both SQLite and PostgreSQL

## [1.0.0] - 2026-01-10

### Added
- Initial arbitrage monitoring system
- Basic database support with SQLite
- Fee analyzer tool
- Time-based analysis
- Exchange analytics
- Rate limiting protection
- Colorized terminal output

### Documentation
- Complete setup guide
- API usage examples
- Deployment instructions
