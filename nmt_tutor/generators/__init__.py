"""Registry of the 40 "identical example" generators.

Subject modules are imported lazily: a generator's module is loaded the first
time one of its keys is requested, so startup does not pay for all of them.
"""

import importlib

from ._common import REGISTRY as DRILL_GENERATORS
from ._common import register_drill  # noqa: F401  (re-export for custom generators)

SUBJECT_GENERATORS = {
    "ukrmova": ["ukrmova_pref_zs", "ukrmova_nagolos", "ukrmova_double", "ukrmova_myak", "ukrmova_rodovyi"],
    "math": ["math_ineq", "math_percent_trip", "math_prob", "math_trap_angle", "math_exp_eq", "math_deriv_ext", "math_vector", "math_module_pow"],
    "history": ["hist_dates_20c", "hist_chrono_17c", "hist_terms_19c"],
    "english": ["eng_verb_agreement", "eng_passive_past", "eng_connectors_whether", "eng_vocab_context", "eng_reading_ads"],
    "german": ["ger_gram_context"],
    "french": ["fr_gram_context"],
    "spanish": ["esp_gram_context"],
    "ukrlit": ["lit_pseudonyms", "lit_genres"],
    "biology": ["bio_dna_percent", "bio_dna_deoxy"],
    "physics": ["phys_free_fall", "phys_incline", "phys_thermo_1law", "phys_humidity", "phys_halflife"],
    "chemistry": ["chem_gas_molar", "chem_solution_sat", "chem_yield", "chem_alkane_combust"],
    "geography": ["geo_map_scale", "geo_azimuth", "geo_ukr_extremes"],
}

_SUBJECT_MODULES = {
    "ukrmova": "ukrmova",
    "math": "maths",
    "history": "history",
    "english": "languages",
    "german": "languages",
    "french": "languages",
    "spanish": "languages",
    "ukrlit": "ukrlit",
    "biology": "biology",
    "physics": "physics",
    "chemistry": "chemistry",
    "geography": "geography",
}

_KEY_TO_SUBJECT = {key: sid for sid, keys in SUBJECT_GENERATORS.items() for key in keys}


def generator_count():
    return len(_KEY_TO_SUBJECT)


def has_generator(key):
    return bool(key) and (key in DRILL_GENERATORS or key in _KEY_TO_SUBJECT)


def get_generator(key):
    """Returns the generator function for a drill_key (importing its module on demand) or None."""
    fn = DRILL_GENERATORS.get(key)
    if fn is None and key in _KEY_TO_SUBJECT:
        importlib.import_module("." + _SUBJECT_MODULES[_KEY_TO_SUBJECT[key]], __name__)
        fn = DRILL_GENERATORS.get(key)
    return fn


def generators_for_subject(subject_id):
    return SUBJECT_GENERATORS.get(subject_id, [])


def load_all():
    """Imports every subject module (used by tests and tools)."""
    for mod in sorted(set(_SUBJECT_MODULES.values())):
        importlib.import_module("." + mod, __name__)
    return DRILL_GENERATORS
