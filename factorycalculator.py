from utils import *
from recipe import Recipe

if TYPE_CHECKING:
    from factory import Factory
    from item import Item

# class FactoryCalculator:
#     def __init__(self):
#         pass


def calculateNormalizedRequirements(factory, reqs, breakdown, top_item):
    # type: (Factory, Mapping[Item, float], Mapping[Item, Mapping[Recipe, float]], Item) -> None
    """
    Calculate the amount of items that are needed within the partition.
    This is normalized since it is unknown how much of this item is
    needed within the full factory.  This will be calculated after the
    partition requirements have been completed.  This starts the
    recursion and handles items that require special calculations

    :param factory: Factory object, used for accessing items and recipes
    """
    # Create a dummy recipe that uses the top item as an ingredient
    # We do this so the top item gets included in the partition requirements
    top_recipe = Recipe(**{"name":"dummy", "ingredients":[[top_item.name, 1]], "result":1})

    # Requirements are calculated initially with a normalized value
    passed_items = recurseCalculateNR(
        factory, reqs, breakdown, top_recipe, 1
    )

    if any(x in factory.calc_exceptions for x in list(passed_items)):
        # This will catch instances where light-oil is needed except for cracking
        if "petroleum-gas" in passed_items:
            calculateVanillaOilRequirements(factory, reqs, breakdown)
            try:
                passed_items.pop("petroleum-gas")
            except:
                pass
            try:
                passed_items.pop("light-oil")
            except:
                pass
            try:
                passed_items.pop("heavy-oil")
            except:
                pass
        else:
            raise AttributeError(
                "If one of the oil products is in exclusion list, petroleum gas must be"
            )

    # Add additional specific handling here for other exceptions
    for passed in passed_items:
        print(passed)


def recurseCalculateNR(factory, reqs, breakdown, recipe, craft_amount):
    # type: (Factory, Mapping[Item, float], Mapping[Item, Mapping[Recipe, float]], Recipe, float) -> dict
    productivity = 1
    if recipe.name in factory.prod_limitations:
        productivity += factory.prod_bonus * recipe.getMaxModules()

    passed_items = {}
    passed = {}
    for ingredient_name in recipe.ingredients.keys():
        ingredient = factory.item_list[ingredient_name]

        # Do not calculate requirements for a solid/fluid that is handled
        # differently, i.e. oil products
        if ingredient_name not in factory.calc_exceptions:
            # This could be put in a loop for recipes that produce more than 1 output
            # This would require the partition requirements to be an Item->Item
            # relationship instead of Item->Recipe.  I don't know the implications
            # of this change.
            try:
                prod_amount = recipe.products[recipe.name]
            except:
                # This will happen for recipes that have special names, i.e. oil
                # and nuclear recipes
                raise TypeError(
                    "I think this is not supposed to happen, product not called recipe name"
                )

            # Calculate the amount of the ingredient needed
            #                        Num recipe crafts * ingredient per craft
            # Amount of ingredient = ----------------------------------------
            #                        Productivity * amount produced per craft
            ingredient_amount = (
                craft_amount
                * recipe.ingredients[ingredient_name]
                / (productivity * prod_amount)
            )

            # Check if data structure is created yet
            if reqs.get(ingredient) is None:
                reqs[ingredient] = ingredient_amount
            else:
                reqs[ingredient] += ingredient_amount

            if breakdown.get(ingredient) is None:
                breakdown[ingredient] = {}

            if breakdown[ingredient].get(recipe) is None:
                breakdown[ingredient][recipe] = ingredient_amount
            else:
                breakdown[ingredient][recipe] += ingredient_amount

            # Do not continue recursion for ingredients that are the top level
            # item of a partition
            if (
                (ingredient not in factory.partitions.keys() or recipe.name == "dummy")
                and not ingredient.is_resource
            ):
                # Only use preferred recipe for an item
                passed = recurseCalculateNR(
                    factory,
                    reqs,
                    breakdown,
                    ingredient.preferred_recipe,
                    ingredient_amount,
                )
                for item in passed.keys():
                    passed_items[item] = 1
        else:
            passed_items[ingredient_name] = 1

    return passed_items


def calculateVanillaOilRequirements(factory, reqs, breakdown):
    # type: (Factory, Mapping[Item, float], Mapping[Item, Mapping[Recipe, float]]) -> None
    heavy = factory.item_list["heavy-oil"]
    light = factory.item_list["light-oil"]
    petro = factory.item_list["petroleum-gas"]
    oil = factory.item_list["crude-oil"]
    water = factory.item_list["water"]

    oil_process = heavy.preferred_recipe

    heavy_requesters = ["lubricant"]
    light_requesters = ["solid-fuel", "rocket-fuel"]
    petro_requesters = ["sulfur", "plastic-bar"]
    # oil_requesters MUST be ordered from top to bottom
    oil_requesters = {
        heavy: heavy_requesters,
        light: light_requesters,
        petro: petro_requesters,
    }

    # Calculate the amount of product from a single oil process craft
    # Heavy oil
    # Get requirement of heavy oil if there is one (coal liquefaction)
    try:
        heavy_req = oil_process.ingredients[heavy.name]
    except:
        heavy_req = 0
    oil_product_per_craft = {heavy: oil_process.products[heavy.name] - heavy_req}

    # Light oil
    light_per_craft = oil_process.products[light.name]
    heavy_ing = light.preferred_recipe.ingredients[heavy.name]
    light_prod = light.preferred_recipe.products[light.name]
    productivity = 1 + factory.prod_bonus * light.preferred_recipe.getMaxModules()
    light_per_craft += (
        oil_product_per_craft[heavy] * light_prod * productivity / heavy_ing
    )
    oil_product_per_craft[light] = light_per_craft

    # Petroleum gas
    petro_per_craft = oil_process.products[petro.name]
    light_ing = petro.preferred_recipe.ingredients[light.name]
    petro_prod = petro.preferred_recipe.products[petro.name]
    productivity = 1 + factory.prod_bonus * petro.preferred_recipe.getMaxModules()
    petro_per_craft += (
        oil_product_per_craft[light] * petro_prod * productivity / light_ing
    )
    oil_product_per_craft[petro] = petro_per_craft

    excess_light = 0
    excess_petro = 0
    # Calculate products needed for oil
    for oil_product in oil_requesters.keys():
        # Add entries for the oil product in requirements
        if reqs.get(oil_product) is None:
            reqs[oil_product] = 0
        if breakdown.get(oil_product) is None:
            breakdown[oil_product] = {}

        # Calculate the needed amount of the oil product
        for requester in oil_requesters[oil_product]:
            # Get the item and recipe of the requester
            req_item = factory.item_list[requester]
            req_recipe = None
            req_recipe = req_item.preferred_recipe
            productivity = 1 + factory.prod_bonus * req_recipe.getMaxModules()

            # Retrieve the needed inputs to calculate the needed ingredient
            if reqs.get(req_item) is not None:
                craft_amount = reqs[req_item]
            else:
                craft_amount = 0

            ing_per_craft = req_recipe.ingredients[oil_product.name]
            prod_per_craft = req_recipe.products[requester]

            oil_prod_req = (
                craft_amount * ing_per_craft / (productivity * prod_per_craft)
            )

            # Add needed oil product to requirements, don't add if 0
            if oil_prod_req > 0:
                reqs[oil_product] += oil_prod_req
                if breakdown[oil_product].get(req_recipe) is None:
                    breakdown[oil_product][req_recipe] = oil_prod_req
                else:
                    breakdown[oil_product][req_recipe] += oil_prod_req

    # There's a limitation here that requires excess products to all be used
    # In order to not need this, some system of equations would need
    # to be solved to handle the excess petro.  Pretty sure it would all just
    # go into solid fuel
    oil_process_crafts = 0
    crafts_ho = reqs[heavy] / oil_product_per_craft[heavy]
    excess_light += crafts_ho * oil_process.products[light.name]
    excess_petro += crafts_ho * oil_process.products[petro.name]
    # assert crafts_ho >= 0

    oil_process_crafts += crafts_ho

    crafts_lo = (reqs[light] - excess_light) / oil_product_per_craft[light]
    excess_petro += crafts_lo * oil_process.products[petro.name]
    # assert crafts_lo >= 0

    oil_process_crafts += crafts_lo

    crafts_pg = (reqs[petro] - excess_petro) / oil_product_per_craft[petro]
    assert crafts_pg >= 0

    oil_process_crafts += crafts_pg

    oil_process_out = {
        heavy: oil_process_crafts * oil_process.products[heavy.name],
        light: oil_process_crafts * oil_process.products[light.name],
        petro: oil_process_crafts * oil_process.products[petro.name],
    }

    productivity = 1 + factory.prod_bonus * oil_process.getMaxModules()
    for ingredient_name in oil_process.ingredients.keys():
        ingredient = factory.item_list[ingredient_name]

        ingredient_amount = (
            oil_process.ingredients[ingredient_name] * oil_process_crafts / productivity
        )

        if reqs.get(ingredient) is None:
            reqs[ingredient] = ingredient_amount
        else:
            reqs[ingredient] += ingredient_amount

        if breakdown.get(ingredient) is None:
            breakdown[ingredient] = {}

        if breakdown[ingredient].get(oil_process) is None:
            breakdown[ingredient][oil_process] = ingredient_amount
        else:
            breakdown[ingredient][oil_process] += ingredient_amount

    heavy_for_cracking = oil_process_out[heavy] - reqs[heavy]
    light_from_cracking = heavy_for_cracking * light_prod * productivity / heavy_ing
    light_for_cracking = oil_process_out[light] + light_from_cracking - reqs[light]
    petro_from_cracking = light_for_cracking * petro_prod * productivity / light_ing
    # This assertion should catch any time the limitation above is broken
    assert abs(oil_process_out[petro] + petro_from_cracking - reqs[petro] < 0.1)

    # Add water requirements for cracking
    heavy_water = (
        light_from_cracking
        * light.preferred_recipe.ingredients[water.name]
        / (productivity * light_prod)
    )
    light_water = (
        petro_from_cracking
        * petro.preferred_recipe.ingredients[water.name]
        / (productivity * petro_prod)
    )
    if reqs.get(water) is None:
        reqs[water] = heavy_water + light_water
    else:
        reqs[water] += heavy_water + light_water

    if breakdown.get(water) is None:
        breakdown[water] = {}

    if breakdown[water].get(light.preferred_recipe) is None:
        breakdown[water][light.preferred_recipe] = heavy_water
    else:
        breakdown[water][light.preferred_recipe] += heavy_water

    if breakdown[water].get(petro.preferred_recipe) is None:
        breakdown[water][petro.preferred_recipe] = light_water
    else:
        breakdown[water][petro.preferred_recipe] += light_water

    # Update requirements of partition
    reqs[heavy] += heavy_for_cracking
    reqs[light] += light_for_cracking
    breakdown[heavy][light.preferred_recipe] = heavy_for_cracking
    breakdown[light][petro.preferred_recipe] = light_for_cracking


def scaleRequirements(reqs, breakdown, rate):
    # type: (Mapping[Item, float], Mapping[Item, Mapping[Recipe, float]], float) -> None
    # Iterate on all items and multiply by rate
    for item in reqs.keys():
        reqs[item] *= rate

    for item in breakdown.keys():
        for recipe in breakdown[item].keys():
            breakdown[item][recipe] *= rate

    # Double check
    for item in reqs.keys():
        total_req = reqs[item]

        summed = 0
        for recipe in breakdown[item].keys():
            summed += breakdown[item][recipe]

        assert abs(total_req - summed) < 0.01
