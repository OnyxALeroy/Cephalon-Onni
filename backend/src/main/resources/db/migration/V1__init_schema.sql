-- Cephalon Onni: initial Postgres schema for the Java rewrite.
--
-- All statements are IF NOT EXISTS: the static catalog + items-branch tables (warframes,
-- weapons, mods, missions, relics, recipes, drop_sources, images, arcanes, amp_parts,
-- companions, resources) may already exist in this database, created at runtime by the old
-- FastAPI backend's SQLAlchemy `Base.metadata.create_all()` (there were no real Alembic
-- version files to port — see backend-rework-plan.md Phase 2). Only users/builds/
-- inventory_items/worldstate_cache are genuinely new.

CREATE TABLE IF NOT EXISTS warframes (
    id SERIAL PRIMARY KEY,
    unique_name VARCHAR UNIQUE,
    name VARCHAR,
    parent_name VARCHAR,
    description TEXT,
    health INTEGER,
    shield INTEGER,
    armor INTEGER,
    stamina INTEGER,
    power INTEGER,
    codex_secret BOOLEAN DEFAULT FALSE,
    mastery_req INTEGER,
    sprint_speed DOUBLE PRECISION,
    passive_description TEXT,
    exalted JSONB,
    abilities JSONB,
    product_category VARCHAR
);
CREATE INDEX IF NOT EXISTS ix_warframes_unique_name ON warframes (unique_name);

CREATE TABLE IF NOT EXISTS weapons (
    id SERIAL PRIMARY KEY,
    unique_name VARCHAR UNIQUE,
    name VARCHAR,
    codex_secret BOOLEAN DEFAULT FALSE,
    critical_chance DOUBLE PRECISION,
    critical_multiplier DOUBLE PRECISION,
    damage_per_shot JSONB,
    description TEXT,
    fire_rate DOUBLE PRECISION,
    mastery_req INTEGER,
    omega_attenuation DOUBLE PRECISION,
    proc_chance DOUBLE PRECISION,
    product_category VARCHAR,
    total_damage INTEGER,
    accuracy DOUBLE PRECISION,
    blocking_angle INTEGER,
    combo_duration INTEGER,
    exclude_from_codex BOOLEAN,
    follow_through DOUBLE PRECISION,
    heavy_attack_damage INTEGER,
    heavy_slam_attack INTEGER,
    heavy_slam_radial_damage INTEGER,
    heavy_slam_radius INTEGER,
    magazine_size INTEGER,
    max_level_cap INTEGER,
    multishot INTEGER,
    noise VARCHAR,
    prime_omega_attenuation DOUBLE PRECISION,
    range DOUBLE PRECISION,
    reload_time DOUBLE PRECISION,
    sentinel BOOLEAN,
    slam_attack INTEGER,
    slam_radial_damage INTEGER,
    slam_radius INTEGER,
    slide_attack INTEGER,
    slot INTEGER,
    trigger VARCHAR,
    wind_up DOUBLE PRECISION
);
CREATE INDEX IF NOT EXISTS ix_weapons_unique_name ON weapons (unique_name);

CREATE TABLE IF NOT EXISTS mods (
    id SERIAL PRIMARY KEY,
    unique_name VARCHAR UNIQUE,
    name VARCHAR,
    polarity VARCHAR,
    rarity VARCHAR,
    type VARCHAR,
    subtype VARCHAR,
    codex_secret BOOLEAN DEFAULT FALSE,
    base_drain INTEGER,
    fusion_limit INTEGER,
    compat_name VARCHAR,
    mod_set VARCHAR,
    mod_set_values JSONB,
    is_utility BOOLEAN,
    description JSONB,
    level_stats JSONB,
    upgrade_entries JSONB,
    available_challenges JSONB
);
CREATE INDEX IF NOT EXISTS ix_mods_unique_name ON mods (unique_name);

CREATE TABLE IF NOT EXISTS missions (
    id SERIAL PRIMARY KEY,
    unique_name VARCHAR UNIQUE,
    mission_name VARCHAR,
    system_name VARCHAR,
    planet VARCHAR,
    type VARCHAR,
    node_type INTEGER,
    faction_index INTEGER,
    mastery_req INTEGER,
    min_enemy_level INTEGER,
    max_enemy_level INTEGER,
    mission_index INTEGER,
    system_index INTEGER,
    drops JSONB
);
CREATE INDEX IF NOT EXISTS ix_missions_unique_name ON missions (unique_name);
CREATE INDEX IF NOT EXISTS ix_missions_mission_name ON missions (mission_name);

CREATE TABLE IF NOT EXISTS relics (
    id SERIAL PRIMARY KEY,
    unique_name VARCHAR UNIQUE,
    name VARCHAR,
    codex_secret BOOLEAN DEFAULT FALSE,
    description TEXT,
    relic_rewards JSONB
);
CREATE INDEX IF NOT EXISTS ix_relics_unique_name ON relics (unique_name);

CREATE TABLE IF NOT EXISTS recipes (
    id SERIAL PRIMARY KEY,
    unique_name VARCHAR UNIQUE,
    build_price INTEGER,
    build_time INTEGER,
    skip_build_time_price INTEGER,
    consume_on_use BOOLEAN,
    num INTEGER,
    codex_secret BOOLEAN DEFAULT FALSE,
    result_type VARCHAR,
    ingredients JSONB
);
CREATE INDEX IF NOT EXISTS ix_recipes_unique_name ON recipes (unique_name);

CREATE TABLE IF NOT EXISTS drop_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    source_type VARCHAR,
    source VARCHAR,
    chance DOUBLE PRECISION,
    rotation VARCHAR,
    CONSTRAINT uq_drop_sources_name_source UNIQUE (name, source)
);
CREATE INDEX IF NOT EXISTS ix_drop_sources_name ON drop_sources (name);

CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    unique_name VARCHAR UNIQUE,
    texture_location VARCHAR
);
CREATE INDEX IF NOT EXISTS ix_images_unique_name ON images (unique_name);

-- From the `items` branch (Phase 0)
CREATE TABLE IF NOT EXISTS arcanes (
    id SERIAL PRIMARY KEY,
    unique_name VARCHAR UNIQUE,
    name VARCHAR,
    codex_secret BOOLEAN DEFAULT FALSE,
    rarity VARCHAR,
    level_stats JSONB
);
CREATE INDEX IF NOT EXISTS ix_arcanes_unique_name ON arcanes (unique_name);

CREATE TABLE IF NOT EXISTS amp_parts (
    id SERIAL PRIMARY KEY,
    unique_name VARCHAR UNIQUE,
    name VARCHAR,
    description VARCHAR,
    codex_secret BOOLEAN DEFAULT FALSE,
    component_type VARCHAR
);
CREATE INDEX IF NOT EXISTS ix_amp_parts_unique_name ON amp_parts (unique_name);

CREATE TABLE IF NOT EXISTS companions (
    id SERIAL PRIMARY KEY,
    unique_name VARCHAR UNIQUE,
    name VARCHAR,
    description VARCHAR,
    health INTEGER,
    shield INTEGER,
    armor INTEGER,
    stamina INTEGER,
    power INTEGER,
    codex_secret BOOLEAN DEFAULT FALSE,
    exclude_from_codex BOOLEAN DEFAULT FALSE,
    product_category VARCHAR
);
CREATE INDEX IF NOT EXISTS ix_companions_unique_name ON companions (unique_name);

CREATE TABLE IF NOT EXISTS resources (
    id SERIAL PRIMARY KEY,
    unique_name VARCHAR UNIQUE,
    name VARCHAR,
    description VARCHAR,
    codex_secret BOOLEAN DEFAULT FALSE,
    parent_name VARCHAR,
    exclude_from_codex BOOLEAN DEFAULT FALSE,
    show_in_inventory BOOLEAN DEFAULT FALSE,
    prime_selling_price INTEGER
);
CREATE INDEX IF NOT EXISTS ix_resources_unique_name ON resources (unique_name);

-- Genuinely new tables (previously in MongoDB)

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    username VARCHAR NOT NULL UNIQUE,
    hashed_password VARCHAR NOT NULL,
    role VARCHAR NOT NULL DEFAULT 'Tenno',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS builds (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    warframe_unique_name VARCHAR NOT NULL,
    warframe_mods JSONB NOT NULL DEFAULT '[]',
    warframe_arcanes JSONB NOT NULL DEFAULT '[]',
    primary_weapon JSONB,
    secondary_weapon JSONB,
    melee_weapon JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_builds_user_id ON builds (user_id);
CREATE INDEX IF NOT EXISTS ix_builds_user_id_created_at ON builds (user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS inventory_items (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    item_key VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    rarity VARCHAR NOT NULL,
    count INTEGER NOT NULL DEFAULT 1,
    rank INTEGER,
    polarity JSONB,
    extra JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_inventory_items_user_id ON inventory_items (user_id);

CREATE TABLE IF NOT EXISTS worldstate_cache (
    id BIGINT PRIMARY KEY,
    etag VARCHAR,
    payload JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
