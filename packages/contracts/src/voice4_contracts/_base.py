from pydantic import BaseModel, ConfigDict


class ContractModel(BaseModel):
    """Base for every cross-service message: immutable, strict about unknown fields,
    bytes travel as URL-safe base64 (RFC 4648 sec. 5) in JSON."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        ser_json_bytes="base64",
        val_json_bytes="base64",
    )
