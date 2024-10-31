def handle_vertical_collision(player, objects, dy):
#     collided_objects = []
#     for obj in objects:
#         if py.sprite.collide_mask(player, obj):
#             if dy > 0:
#                 player.rect.bottom = obj.rect.top
#                 player.landed()
#             elif dy < 0:
#                 player.rect.top = obj.rect.bottom
#                 player.hit_head() 

#             collided_objects.append(obj)

#     return collided_objects