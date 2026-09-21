# 22.0.0 "aurostibite-ambulance" (2026-06-03)
## Breaking Changes
### aria
- The legacy combobox and autocomplete implementations have been removed. Use the new standalone combobox instead.
### cdk
- * `ContextMenuTracker` has been renamed to `MenuTracker`.
- * The `event` parameter of `DropListRef.drop` is now required.
### material
- * `MatListOption.checkboxPosition` has been removed. use `togglePosition` instead.
 * `MatListOptionCheckboxPosition` has been renamed to `MatListOptionTogglePosition`.
- * `ArrowViewState` has been removed.
### multiple
- Renames the values input/model to value in Combobox, Listbox, Tree, Menu, Toolbar, and Select. Users must update their templates to use the value property instead of values.
### google-maps
| Commit | Type | Description |
| -- | -- | -- |
| e44ff8318 | feat | Add support for the gmp-click event (#33147) |

# 21.2.0 "plastic-lion" (2026-02-25)
No user facing changes in this release
