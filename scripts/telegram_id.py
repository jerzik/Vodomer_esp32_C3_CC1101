"""Extract the BCD address from a CRC-stripped Wireless M-Bus link frame."""

import argparse
import re


def extract_id(frame: str) -> str:
    """Use L,C,M[2],A[6] framing; do not guess a raw/CRC-containing format."""
    text = frame.strip()
    if text.startswith("0x"):
        text = text[2:]
    text = re.sub(r"\s+", "", text)
    if len(text) % 2 or not re.fullmatch(r"[0-9a-fA-F]+", text):
        raise ValueError("Zadejte pouze úplný HEX řetězec rámce (bez logového prefixu).")
    data = bytes.fromhex(text)
    if len(data) < 10 or len(data) != data[0] + 1:
        raise ValueError(
            "Očekávám linkový rámec bez blokových CRC: délka musí být L+1, alespoň 10 bajtů."
        )
    digits = data[4:8][::-1].hex().upper()
    if not digits.isdecimal():
        raise ValueError("Identifikátor není platné osmimístné BCD číslo.")
    return digits


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "frame",
        help="HEX CRC-stripped rámce začínajícího L,C,M,A; skript neověřuje CRC, AES ani příslušnost měřidla",
    )
    args = parser.parse_args()
    try:
        print(f"Rádiové ID: {extract_id(args.frame)} (nutno porovnat se štítkem)")
    except ValueError as err:
        parser.error(str(err))


if __name__ == "__main__":
    main()
