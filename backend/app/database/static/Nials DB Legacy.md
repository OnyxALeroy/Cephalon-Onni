# Database Format ?

## Main Item table


item_id (uint64_t) | item_type (enum item_type) | is_prime (bool)

## Name table

item_id (uint64_t) | language_id (to be decided) | name (string)

## Schematic table

schematic_id (from item_id) | vec<item_id, quantity> | credit_cost (uint64_t) | duration (uint64_t)| out_item_id (uint64_t) | out_item_quantity (uint64_t) 

The second field is a vector of length bewteen 0 (maybe 1) and 4, it is the items used in the recipe and their quantity.

## Droptable table

droptable_id | item_id | quantity | proba

The format is, for one droptable, for every item it can drop there is a different line.
With this droptable as an example :

example_droptable :
id = 0

* P(item_1)  = 10%, quantity(item_1) = 3
* P(item_1)  = 05%, quantity(item_1) = 2
* P(item_2)  = 50%, quantity(item_2) = 2
* P(item_3)  = 25%, quantity(item_3) = 5
* P(nothing) = 10%

id(item_1) = 25
id(item_2) = 46
id(item_3) = 75

This will look like this in the db :

0 | 25 | 3 | 15
0 | 25 | 2 | 5
0 | 46 | 2 | 50
0 | 75 | 5 | 25


The sum of the probabilities may be slightly above 100% because they are the ones on the offical droptables.

## Relic Table

relic_id (linked_to_item_id) | droptable_id

Each relic has it's own droptable (I hate formas that can drop in two, they force me to do things properly)

## Other

enum item_type {
  equippable,
  arsenal_wheel,
  schematic,
  base_item,
  relic,
  mod,
}
