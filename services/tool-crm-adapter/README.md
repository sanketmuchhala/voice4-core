# tool-crm-adapter

**Owner:** Sanket (Claude Code)

This service runs the COD tools (`get_order`, `update_order_status`, `transfer_to_human`) behind `ToolCallRequest` and `ToolCallResult`, and normalizes structured entities to Roman/ASCII.

- `normalize.py` is implemented and tested. It handles order IDs, Indian mobile numbers and amounts, including Devanagari digits.
- The tool handlers and the merchant-store webhook client are still TODO.
