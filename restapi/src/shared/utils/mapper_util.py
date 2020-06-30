

import copy


def formart_id_with_entitites(entities: []):
    if entities is None and len(entities) == 0:
        return
    for entity in entities:
        entity["id"] = entity["_id"]
        entity.pop("_id")

def formart_id_with_entity(entity):
    
    cloneEntity = copy.deepcopy(entity)
    
    if entity is None:
        return None
    
    cloneEntity["id"] = cloneEntity["_id"]
    cloneEntity.pop("_id")
    
    return cloneEntity
    