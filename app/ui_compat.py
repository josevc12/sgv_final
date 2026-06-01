import flet as ft


def padding_symmetric(horizontal, vertical):
    try:
        return ft.Padding.symmetric(horizontal=horizontal, vertical=vertical)
    except AttributeError:
        return ft.padding.symmetric(horizontal=horizontal, vertical=vertical)


def padding_all(value):
    try:
        return ft.Padding.all(value)
    except AttributeError:
        return ft.padding.all(value)


def border_radius_only(top_left=0, top_right=0, bottom_left=0, bottom_right=0):
    try:
        return ft.BorderRadius.only(
            top_left=top_left, top_right=top_right,
            bottom_left=bottom_left, bottom_right=bottom_right,
        )
    except AttributeError:
        return ft.border_radius.only(
            top_left=top_left, top_right=top_right,
            bottom_left=bottom_left, bottom_right=bottom_right,
        )
