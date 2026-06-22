# fheroes2 `.fh2m` map format (reverse-engineered, version 13)

Reverse-engineered from fheroes2 source (`src/engine/serialize.{h,cpp}`,
`src/fheroes2/maps/map_format_info.{h,cpp}`, `src/fheroes2/resource/resource.cpp`,
`src/engine/zzlib.cpp`). This is the reference for `kidquest_fh2m`.

## File layout
```
"h2map\0"                         6 bytes magic
<BaseMapFormat>                   uncompressed, big-endian
<zlib stream>                     plain zlib (compress2/uncompress, no framing)
                                  -> decompresses to <MapFormat body>
```
All integers big-endian. The body is a single zlib stream appended after the
header. fheroes2 reads it with size-agnostic `uncompress`, so a re-zlib'd body
need not be byte-identical — only the *uncompressed* body must match.

## Primitive encodings (StreamBase, bigendian)
- `bool`/`int8`/`uint8`           : 1 byte
- `int16`/`uint16`                : 2 bytes BE
- `int32`/`uint32`                : 4 bytes BE
- `string`                        : `uint32` length + raw UTF-8 bytes
- `vector<T>`/`list<T>`           : `uint32` count + elements
- `array<T,N>`                    : `uint32` count (== N) + N elements
- `map<K,V>`                      : `uint32` count + (K,V) pairs
- `optional<T>`                   : `bool` present + T if present
- `pair<A,B>`                     : A then B
- `enum`                          : its underlying integer type
- `Point`                         : `int32` x, `int32` y

## BaseMapFormat (uncompressed header, in order)
`version u16` (==13), `isCampaign bool`, `difficulty u8`,
`availablePlayerColors u8`, `humanPlayerColors u8`, `computerPlayerColors u8`,
`alliances vector<u8>`, `playerRace array<u8,6>`,
`victoryConditionType u8`, `isVictoryConditionApplicableForAI bool`,
`allowNormalVictory bool`, `victoryConditionMetadata vector<u32>`,
`lossConditionType u8`, `lossConditionMetadata vector<u32>`,
`width i32`, `mainLanguage u8` (SupportedLanguage enum:uint8),
`name string`, `description string`, `creatorNotes string` (v>=9),
`translations map<u8, TranslationBaseMapMetadata>` (v>=11;
  `TranslationBaseMapMetadata = name string, description string, creatorNotes string`).

## MapFormat body (zlib-decompressed, in order)
1. `additionalInfo  vector<u32>`
2. `tiles           vector<TileInfo>` (length == width*width)
3. `dailyEvents     vector<DailyEvent>`
4. `rumors          vector<string>`
5. `castleMetadata  map<u32, CastleMetadata>`
6. `heroMetadata    map<u32, HeroMetadata>`
7. `sphinxMetadata  map<u32, SphinxMetadata>`      ← educational riddles
8. `signMetadata    map<u32, SignMetadata>`        ← sign/event text
9. `adventureMapEventMetadata map<u32, AdventureMapEventMetadata>`  ← reward events
10. `selectionObjectMetadata   map<u32, SelectionObjectMetadata>`
11. `capturableObjectsMetadata map<u32, CapturableObjectMetadata>`
12. `monsterMetadata           map<u32, MonsterMetadata>`
13. `artifactMetadata          map<u32, ArtifactMetadata>`
14. `resourceMetadata          map<u32, ResourceMetadata>`
15. `translationInfo           map<u8, TranslationFormat>`

## Structs (field order = serialization order)
- `Funds` = `wood i32, mercury i32, ore i32, sulfur i32, crystal i32, gems i32, gold i32`
- `TileObjectInfo` = `id u32, group u8` (ObjectGroup enum:uint8)`, index u32`
- `TileInfo` = `terrainIndex u16, terrainFlags u8, objects vector<TileObjectInfo>`
- `DailyEvent` = `message string, humanPlayerColors u8, computerPlayerColors u8, firstOccurrenceDay u32, repeatPeriodInDays u32, resources Funds`
- `CastleMetadata` = `customName string, defenderMonsterType array<i32,5>, defenderMonsterCount array<i32,5>, customBuildings bool, builtBuildings vector<u32>, bannedBuildings vector<u32>, mustHaveSpells map<u8,i32>, bannedSpells vector<i32>, availableToHireMonsterCount array<i32,6>`
- `HeroMetadata` = `customName string, customPortrait i32, armyMonsterType array<i32,5>, armyMonsterCount array<i32,5>, artifact array<i32,14>, artifactMetadata array<i32,14>, availableSpells vector<i32>, isOnPatrol bool, patrolRadius u8, secondarySkill array<i8,8>, secondarySkillLevel array<u8,8>, customLevel i16, customExperience i32, customAttack i16, customDefense i16, customKnowledge i16, customSpellPower i16, magicPoints i16, race u8`
- `SphinxMetadata` = `riddle string, answers vector<string>, artifact i32, artifactMetadata i32, resources Funds`
- `SignMetadata` = `message string`
- `AdventureMapEventMetadata` = `message string, humanPlayerColors u8, computerPlayerColors u8, isRecurringEvent bool, artifact i32, artifactMetadata i32, resources Funds, attack i16, defense i16, knowledge i16, spellPower i16, experience i32, secondarySkill u8, secondarySkillLevel u8, monsterType i32, monsterCount i32`
- `SelectionObjectMetadata` = `selectedItems vector<i32>`
- `CapturableObjectMetadata` = `ownerColor u8` (PlayerColor)
- `MonsterMetadata` = `count i32, joinCondition i32, isWeeklyGrowthDisabled bool, selected vector<i32>`
- `ArtifactMetadata` = `radius i32, captureCondition i32, selected vector<i32>`
- `ResourceMetadata` = `count i32`
- `TranslationFormat` = `dailyEvents vector<string>, rumors vector<string>, castleMetadata map<u32,string>, heroMetadata map<u32,string>, sphinxMetadata map<u32,TranslationSphinxMetadata>, signMetadata map<u32,string>, adventureMapEventMetadata map<u32,string>` (`TranslationSphinxMetadata = riddle string, answers vector<string>`)

## What we patch
- **Educational**: `sphinxMetadata` (riddle + answers + reward Funds/artifact), `signMetadata`, `adventureMapEventMetadata`.
- **Persistence** (carry hero/army between daily maps): the player's starting hero
  `HeroMetadata` (`armyMonsterType/Count`, `artifact`, `customLevel`/`customExperience`).
- **Difficulty**: `monsterMetadata` counts, starting `resourceMetadata`, castle armies.
