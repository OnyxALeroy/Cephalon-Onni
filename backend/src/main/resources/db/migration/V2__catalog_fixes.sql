-- Static catalog fixes for the Java importer (com.cephalononni.catalog), plus one users fix.
-- Flyway (V1 + this file) is now the only owner of the schema: nothing else creates tables.

-- users.role holds the wire values ("Tenno", "Administrator"), matching V1's default and the
-- legacy data. Rows written by the Java backend before UserRoleConverter held enum names.
UPDATE users SET role = CASE role
    WHEN 'TENNO' THEN 'Tenno'
    WHEN 'ADMINISTRATOR' THEN 'Administrator'
    WHEN 'TRAVELLER' THEN 'Traveller'
    ELSE role END
WHERE role IN ('TENNO', 'ADMINISTRATOR', 'TRAVELLER');

-- Admin-editable runtime settings (currently: the catalog importer's source URLs). A missing row
-- means "use the default from application.yml".
CREATE TABLE IF NOT EXISTS app_settings (
    setting_key VARCHAR PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_by_user_id BIGINT REFERENCES users (id) ON DELETE SET NULL
);

-- One drop row per (item, source, rotation): the old (name, source) key kept only the first
-- rotation of every mission/key/bounty an item drops from.
ALTER TABLE drop_sources DROP CONSTRAINT IF EXISTS uq_drop_sources_name_source;
ALTER TABLE drop_sources
    ADD CONSTRAINT uq_drop_sources_name_source_rotation UNIQUE NULLS NOT DISTINCT (name, source, rotation);

-- Repair rows written by the legacy Python seeder, which json.dumps()'d values into SQLAlchemy
-- JSON columns and so stored every array/object as a JSON *string* ("[...]"). Only strings that
-- look like an encoded array/object are unwrapped; genuine JSON strings are left alone.
DO $$
DECLARE
    target RECORD;
BEGIN
    FOR target IN
        SELECT * FROM (VALUES
            ('warframes', 'exalted'), ('warframes', 'abilities'),
            ('weapons', 'damage_per_shot'),
            ('mods', 'mod_set_values'), ('mods', 'description'), ('mods', 'level_stats'),
            ('mods', 'upgrade_entries'), ('mods', 'available_challenges'),
            ('missions', 'drops'),
            ('relics', 'relic_rewards'),
            ('recipes', 'ingredients'),
            ('arcanes', 'level_stats')
        ) AS t(table_name, column_name)
    LOOP
        EXECUTE format(
            'UPDATE %I SET %I = (%I #>> ''{}'')::jsonb '
            'WHERE jsonb_typeof(%I) = ''string'' AND (%I #>> ''{}'') ~ ''^\s*[\[{]''',
            target.table_name, target.column_name, target.column_name,
            target.column_name, target.column_name);
    END LOOP;
END $$;
