from datetime import datetime
from enum import Enum
from typing import Dict, List, Tuple

from pydantic import BaseModel


class Plateform(str, Enum):
    PLATFORM_CROSS_PLATFORM = "Cross Platform"
    PLATFORM_SWITCH = "Switch"
    PLATFORM_PC = "PC"
    PLATFORM_XBOX = "Xbox"
    PLATFORM_PLAYSTATION = "PlayStation"


class MissionType(str, Enum):
    rescue = "Rescue"
    assault = "Assault"
    assassination = "Assassination"
    mobile_defense = "Mobile Defense"
    defense = "Defense"
    survival = "Survival"
    disruption = "Disruption"
    exterminate = "Exterminate"
    interception = "Interception"
    hijack = "Hijack"
    sabotage = "Sabotage"
    spy = "Spy"
    defection = "Defection"


class SortieModifier(str, Enum):
    fire = "Fire"
    radiation_hazard = "Radiation Hazard"
    energy_reduction = "Energy Reduction"
    augmented_enemy_armor = "Augmented Enemy Armor"
    augmented_enemy_shields = "Augmented Enemy Shields"
    enemy_elemental_enhancement = "Enemy Elemental Enhancement"
    enemy_physical_enhancement = "Enemy Physical Enhancement"
    enemy_speed_boost = "Enemy Speed Boost"
    eximus_stronghold = "Eximus Stronghold"
    weapon_type_only = "Weapon Type Only"
    electromagnetic_anomalies = "Electromagnetic Anomalies"


class Syndicate(str, Enum):
    steel_meridian = "Steel Meridian"
    SteelMeridianSyndicate = "Steel Meridian"
    CephalonSudaSyndicate = "Cephalon Suda"
    PerrinSyndicate = "The Perrin Sequence"
    ArbitersSyndicate = "Arbiters of Hexis"
    RedVeilSyndicate = "Red Veil"
    NewLokaSyndicate = "New Loka"
    VoxSyndicate = "Vox Solaris"
    QuillsSyndicate = "The Quills"
    AssassinsSyndicate = "The Assassins"
    VentKidsSyndicate = "Ventkids"
    EventSyndicate = "Operational Supply"
    NecraloidSyndicate = "Necraloid"
    CetusSyndicate = "Ostron"
    SolarisSyndicate = "Solaris United"
    EntratiSyndicate = "Entrati"
    ZarimanSyndicate = "The Holdfasts"
    RadioLegionSyndicate = "Nightwave Series 1"
    RadioLegion2Syndicate = "Nightwave Series 2"
    RadioLegion3Syndicate = "Nightwave Series 3"
    RadioLegionIntermissionSyndicate = "Nightwave Intermission"
    RadioLegionIntermission2Syndicate = "Nightwave Intermission 2"
    RadioLegionIntermission3Syndicate = "Nightwave Intermission 3"
    RadioLegionIntermission4Syndicate = "Nightwave: Nora's Choice"
    RadioLegionIntermission5Syndicate = "Nightwave: Nora's Mix Volume 1"
    RadioLegionIntermission6Syndicate = "Nightwave: Nora's Mix Volume 2"
    RadioLegionIntermission7Syndicate = "Nightwave: Nora's Mix Volume 3"


class RelicEra(str, Enum):
    lith = "Lith"
    meso = "Meso"
    neo = "Neo"
    axi = "Axi"
    requiem = "Requiem"
    omnia = "Omnia"


class BoostType(str, Enum):
    affinity = "Affinity"
    credits = "Credits"
    resources = "Resources"


class Faction(str, Enum):
    grineer = "Grineer"
    corpus = "Corpus"
    infested = "Infested"


class ConclaveChallengeCategory(str, Enum):
    daily = "Daily"
    weekly = "Weekly"
    weekly_root = "Weekly Root"


class PVPMode(str, Enum):
    all = "All"
    capture_the_flag = "Capture the Flag"
    deathmatch = "Deathmatch"
    team_deathmatch = "Team Deathmatch"
    speed_ball = "Speedball"
    none = "None"


# -------------------------------------------------------------------------------------------------


class MissionRewardItem(BaseModel):
    item_type: str
    item_count: int


class MissionReward(BaseModel):
    credits: int
    counted_items: List[MissionRewardItem]


class MissionChallenge(BaseModel):
    _id: str
    activation: datetime
    challenge: str
    daily: bool
    expiry: datetime


# -------------------------------------------------------------------------------------------------


class MissionInfo(BaseModel):
    location: str
    mission_type: str
    faction: str
    difficulty: int
    mission_reward: dict
    level_override: str
    enemy_spec: str
    min_enemy_level: int
    max_enemy_level: int
    desc_text: str
    max_wave_num: int


class Event(BaseModel):
    name: str


class Alert(BaseModel):
    _id: str
    name: str
    activation: datetime
    expiry: datetime
    mission_info: MissionInfo
    tag: str
    force_unlock: bool


class SyndicateMission(BaseModel):
    mission: str
    syndicate: Syndicate


class VoidFissure(BaseModel):
    mission: str
    era: RelicEra


# -------------------------------------------------------------------------------------------------


class SortieMission(BaseModel):
    type: MissionType
    modifier: SortieModifier
    mission: str
    tileset: str


class Sortie(BaseModel):
    _id: str
    activation: datetime
    expiration: datetime
    boss: str
    extra_drops: list
    seed: int
    missions: List[SortieMission]


class Invasion(BaseModel):
    _id: str
    mission: str
    loc_tag: str
    activation: datetime
    attacker_faction: Faction
    defender_faction: Faction
    attacker_reward: List[MissionRewardItem]
    defender_reward: List[MissionRewardItem]


class VoidTrader(BaseModel):
    _id: str
    activation: datetime
    expiry: datetime
    node: str
    character: str


class PrimeResurgenceItem(BaseModel):
    ItemType: str
    PrimePrice: int


class PrimeResurgenceScheduleInfo(BaseModel):
    Expiry: datetime
    FeaturedItem: str


class PrimeResurgence(BaseModel):
    _id: str
    activation: datetime
    completed: bool
    initial_start_date: datetime
    mission: str
    manifest: List[PrimeResurgenceItem]
    expiry: datetime
    evergreen_manifest: List[PrimeResurgenceItem]
    schedule_info: List[PrimeResurgenceScheduleInfo]


class VoidStorm(BaseModel):
    _id: str
    activation: datetime
    expiration: datetime
    era: RelicEra
    mission: str


class DailyDeal(BaseModel):
    activation: datetime
    expiration: datetime
    original_price: int
    sale_price: int
    item: str
    sold_amount: int
    total_amount: int


class ConclaveChallenge(BaseModel):
    _id: str
    activation: datetime
    expiration: datetime
    category: ConclaveChallengeCategory
    pvp_mode: PVPMode
    challenge_type_id: str
    challenge_sub_challenges: List[str]


class FeaturedDojo(BaseModel):
    _id: str
    alliance_id: str
    has_emblem: bool
    platforms: Dict[Plateform, bool]
    icon_override: int
    name: str
    tier: int


class SeasonInfo(BaseModel):
    _id: str
    activation: datetime
    expiration: datetime
    active_challenges: List[MissionChallenge]
    affiliation_tag: str
    parameters: str
    phase: int
    season: int


# -------------------------------------------------------------------------------------------------


class WorldState(BaseModel):
    world_seed: str
    api_version: str
    mobile_version: str
    date: datetime
    current_event: Event
    current_alerts: List[Alert]
    sortie: Sortie
    syndicate_missions: List[SyndicateMission]
    void_fissures: List[VoidFissure]
    global_boosts: List[BoostType]
    void_trader: VoidTrader
    prime_resurgence: PrimeResurgence
    prime_token_availability: bool
    daily_deals: List[DailyDeal]
    pvp_alternative_modes: list
    pvp_active_tournaments: list
    invasion_construction_statuses: Tuple[float, float]
    feature_dojos: List[FeaturedDojo]
    season_info: SeasonInfo
