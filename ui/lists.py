import bpy


class BAKERY_UL_texture_sets(bpy.types.UIList):
    # draw each texture set row.
    # keep list rows compact: icon + name.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.prop(item, "enabled", text="")
        row.label(icon="IMAGE_DATA")
        row.prop(item, "name", text="", emboss=False)


class BAKERY_UL_low_polys(bpy.types.UIList):
    # draw each target row.
    # expose a quick select button and an object search per row.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        op = row.operator("bakery.select_object", text="", icon="MESH_DATA", emboss=False)
        op.object_name = item.object.name if item.object else ""
        op.list_kind = "LOW"
        op.item_index = index
        row.prop_search(item, "object", context.scene, "objects", text="", icon="VIEWZOOM")


class BAKERY_UL_high_polys(bpy.types.UIList):
    # draw each source row.
    # Sources mirror the targets list layout for consistency.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        op = row.operator("bakery.select_object", text="", icon="MESH_DATA", emboss=False)
        op.object_name = item.object.name if item.object else ""
        op.list_kind = "HIGH"
        op.item_index = index
        row.prop_search(item, "object", context.scene, "objects", text="", icon="VIEWZOOM")


class BAKERY_UL_bake_targets(bpy.types.UIList):
    # draw each bake target row.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.prop(item, "enabled", text="")
        row.label(icon="IMAGE_PLANE")
        row.prop(item, "name", text="", emboss=False)
