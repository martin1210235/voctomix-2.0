# Voctomix Transitions

Voctomix 2.0 keeps the transition engine inherited from the C3VOC `voctomix2`
branch and configures the transition graph through `voctocore/default-config.ini`.

## Current Composite Identifiers

The shipped configuration defines these operator-facing composite modes:

| Identifier | Meaning |
|---|---|
| `fs` | Full-screen channel A |
| `sbs` | Side-by-side layout |
| `pip` | Picture-in-picture layout |
| `lec` | Lecture layout |
| `lec_43` | Lecture layout variant |

Some modes also have mirrored variants through the `|` modifier, for example
`|pip` and `|lec`, as configured in `voctogui/default-config.ini`.

## Control Commands

The modern control path uses composite-command strings:

```text
cut fs(cam1,*)
transition sbs(cam1,cam2)
transition pip(cam1,cam2)
transition lec(cam1,cam2)
```

The command parser accepts:

- `mode(sourceA,sourceB)`, for example `sbs(cam1,cam2)`
- `mode(sourceA)`, when only channel A is supplied
- `mode`, when only the composite mode changes

Use `cut` for an immediate switch and `transition` for an animated transition.

## Configuration

Transition geometry and timing live in:

- `voctocore/default-config.ini`, sections `[composites]` and `[transitions]`
- `voctogui/default-config.ini`, section `[toolbar.composites]`

Keep these files aligned: if a composite is exposed in the GUI, it must exist in
the core configuration.

## Tester

The legacy transition tester is still available:

```bash
cd voctocore
python3 test-transition.py --help
```

It is useful for inspecting configured composites and generated transition
tables, but the runtime source of truth remains `voctocore/default-config.ini`.
