"""Order UID and EIP-712 order struct hashing — port of model/order.rs."""

from __future__ import annotations

from dataclasses import dataclass

from cow_bytes_hex import decode_hex, encode_prefixed
from eth_utils import to_checksum_address

from cow_model.eip712 import hashed_eip712_message, keccak256
from cow_model.order import (
    BuyTokenDestination,
    OrderCreation,
    OrderKind,
    SellTokenSource,
)

# GPv2Order.TYPE_HASH from cowprotocol/contracts v1.1.2
ORDER_TYPE_HASH = bytes.fromhex(
    "d5a25ba2e97094ad7d83dc28a6572da797d6b3e7fc6663bd93efb789fc17e489"
)

KIND_SELL = bytes.fromhex("f3b277728b3fee749481eb3e0b3b48980dbbab78658fc419025cb16eee346775")
KIND_BUY = bytes.fromhex("6ed88e868af0a1983e3886d5f3e95a2fafbd6c3450bc229e27342283dc429ccc")

BALANCE_ERC20 = bytes.fromhex("5a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc9")
BALANCE_EXTERNAL = bytes.fromhex("abee3b73373acd583a130924aad6dc38cfdc44ba0555ba94ce2ff63980ea0632")
BALANCE_INTERNAL = bytes.fromhex("4ac99ace14ee0a5ef932dc609df0943ab7ac16b7583634612f8dc35a4289a6ce")


def _address_to_slot(address: str) -> bytes:
    addr = decode_hex(to_checksum_address(address)[2:])
    slot = bytearray(32)
    slot[12:32] = addr
    return bytes(slot)


def _u256_to_slot(value: int) -> bytes:
    return value.to_bytes(32, byteorder="big")


def _parse_app_data_hash(app_data: str) -> bytes:
    if app_data.startswith("0x"):
        raw = decode_hex(app_data)
    else:
        raw = app_data.encode()
    if len(raw) != 32:
        raise ValueError("app_data must be 32 bytes")
    return raw


def _kind_bytes(kind: OrderKind) -> bytes:
    return KIND_SELL if kind == OrderKind.SELL else KIND_BUY


def _sell_balance_bytes(source: SellTokenSource) -> bytes:
    if source == SellTokenSource.ERC20:
        return BALANCE_ERC20
    if source == SellTokenSource.EXTERNAL:
        return BALANCE_EXTERNAL
    return BALANCE_INTERNAL


def _buy_balance_bytes(dest: BuyTokenDestination) -> bytes:
    return BALANCE_ERC20 if dest == BuyTokenDestination.ERC20 else BALANCE_INTERNAL


def hash_order_struct(order: OrderCreation) -> bytes:
    """EIP-712 hashStruct for GPv2Order — must match Rust OrderData::hash_struct."""
    data = bytearray(416)
    data[0:32] = ORDER_TYPE_HASH
    data[44:64] = _address_to_slot(order.sell_token)[12:32]
    data[76:96] = _address_to_slot(order.buy_token)[12:32]
    receiver = order.receiver or "0x0000000000000000000000000000000000000000"
    data[108:128] = _address_to_slot(receiver)[12:32]
    data[128:160] = _u256_to_slot(int(order.sell_amount))
    data[160:192] = _u256_to_slot(int(order.buy_amount))
    data[220:224] = int(order.valid_to).to_bytes(4, byteorder="big")
    data[224:256] = _parse_app_data_hash(order.app_data)
    data[256:288] = _u256_to_slot(int(order.fee_amount))
    data[288:320] = _kind_bytes(order.kind)
    data[351] = 1 if order.partially_fillable else 0
    data[352:384] = _sell_balance_bytes(order.sell_token_balance)
    data[384:416] = _buy_balance_bytes(order.buy_token_balance)
    return keccak256(bytes(data))


@dataclass(frozen=True)
class ComputedOrderUid:
    """56-byte order UID: 32-byte digest ‖ 20-byte owner ‖ 4-byte validTo."""

    value: bytes

    def __post_init__(self) -> None:
        if len(self.value) != 56:
            raise ValueError("order uid must be 56 bytes")

    @classmethod
    def from_parts(cls, order_digest: bytes, owner: str, valid_to: int) -> ComputedOrderUid:
        if len(order_digest) != 32:
            raise ValueError("order digest must be 32 bytes")
        owner_bytes = decode_hex(to_checksum_address(owner)[2:])
        uid = bytearray(56)
        uid[0:32] = order_digest
        uid[32:52] = owner_bytes
        uid[52:56] = int(valid_to).to_bytes(4, byteorder="big")
        return cls(bytes(uid))

    @classmethod
    def compute(
        cls, order: OrderCreation, domain_separator: bytes, owner: str
    ) -> ComputedOrderUid:
        struct_hash = hash_order_struct(order)
        digest = hashed_eip712_message(domain_separator, struct_hash)
        return cls.from_parts(digest, owner, order.valid_to)

    def to_hex(self) -> str:
        return encode_prefixed(self.value)

    def parts(self) -> tuple[bytes, str, int]:
        digest = self.value[0:32]
        owner = to_checksum_address("0x" + self.value[32:52].hex())
        valid_to = int.from_bytes(self.value[52:56], byteorder="big")
        return digest, owner, valid_to


def compute_order_uid(order: OrderCreation, domain_separator: bytes, owner: str) -> str:
    """Compute the canonical 0x-prefixed order UID hex string."""
    return ComputedOrderUid.compute(order, domain_separator, owner).to_hex()
