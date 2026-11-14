# IntelCPUID

Which Intel processors stand behind a CPUID — the processor signature a
microcode update names — and which microcode updates serve several CPUIDs.
[ByteRipper](https://github.com/maxshevelev/ByteRipper)'s FIT panel reads both
files from here at run time, so a push reaches every copy of the app without a
new build.

| File | What it holds |
|---|---|
| [`IntelCPUIDBrandNames.json`](IntelCPUIDBrandNames.json) | CPUID → code names, cores, product families, steppings, segments, and the models sold with it, each with the S-SPEC codes it was sold under |
| [`IntelMicrocodeSignatures.json`](IntelMicrocodeSignatures.json) | the microcode updates whose extended signature table names more than one CPUID, read from the files of [platomav/CPUMicrocodes](https://github.com/platomav/CPUMicrocodes) |

The table can be searched in a browser — by CPUID, model, S-SPEC, code name or
stepping — at <https://maxshevelev.github.io/IntelCPUID/>: [`index.html`](index.html),
one static page served by GitHub Pages from this branch, which reads
`IntelCPUIDBrandNames.json` beside it. Russian or English, by the browser's
preference.

Both carry `"formatVersion": 1`. ByteRipper refuses a file of a newer format, or
one it cannot decode, and keeps the last pair it read whole; it has no copy of
its own.

## Where the data comes from

Nothing is typed in by hand. The base is the CPUID table of the article
[Применение CPUID на практике…](https://comsystem-tlt.ru/obzori/primenenie-cpuid-na-praktike-dlja-zameni-soc--kombajnov-);
the rest comes from Intel's own pages and documents — the ARK ordering tabs,
the microcode release notes of
[Intel-Linux-Processor-Microcode-Data-Files](https://github.com/intel/Intel-Linux-Processor-Microcode-Data-Files),
the list of processors by CPUID in Intel's security guidance, specification
updates and product change notifications — and from Wikipedia's processor
lists, coreboot's `cpu_ids.h` and the Linux kernel's `intel-family.h`. Every
code added to the article's says where it came from (`sSpecSource`), and every
record behind it keeps its page:

```
Skills/update-cpuid-brand-names/scripts/ark-sspec.json      what ARK's ordering tabs say, model by model
Skills/update-cpuid-brand-names/scripts/found-sspec.json    codes from Intel documents and other sources, with quotes
Skills/update-cpuid-brand-names/scripts/extra-entries.json  CPUIDs the article lacks, each fact with its page
```

## Updating

Two Claude Code skills, stdlib Python only; a run is a diff to read.

- [`Skills/update-cpuid-brand-names`](Skills/update-cpuid-brand-names/SKILL.md) —
  regenerate both files: `scripts/import.py` (the table) and
  `scripts/microcode_signatures.py` (the shared updates), then
  `scripts/check.py` before committing.
- [`Skills/find-sspec`](Skills/find-sspec/SKILL.md) — search for the S-SPECs
  the table still lacks, for the CPUIDs named.

For `/update-cpuid-brand-names` and `/find-sspec` in a local Claude Code
session, link them once (not committed):

```sh
mkdir -p .claude/skills
ln -s ../../Skills/update-cpuid-brand-names .claude/skills/update-cpuid-brand-names
ln -s ../../Skills/find-sspec .claude/skills/find-sspec
```

Commit, then push: the push is the release.
