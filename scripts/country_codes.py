# AFIDA-Watch Country Code Reference Table v1.0
# Canonical adversary nation definitions
# Source: AFIDA country code reference + ISO 3166-1 numeric

ADVERSARY_CODES = {
    156: 'CHINA',
    364: 'IRAN',
    643: 'RUSSIA',
    408: 'NORTH KOREA'
}

AMBIGUITY_CODES = {
    998: 'NO FOREIGN INVESTOR LISTED',
    999: 'NO PREDOMINANT COUNTRY CODE'
}

# Precedence rule:
# 1. If Country Code is not null and not in {998, 999} — use code-based mapping
# 2. Else fall back to normalized Country string
# 3. Else classify as AmbiguousCountry — NOT adversary

PRECEDENCE_RULE = """
AdversaryNation_DirectOwner_CodeBased_v1:
- Primary: Country Code numeric in {156, 364, 643, 408}
- Fallback: Country string normalized in {CHINA, IRAN, RUSSIA, NORTH KOREA}
- Exclusion: Country Code in {998, 999} = AmbiguousCountry, not adversary
"""
