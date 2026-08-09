# Universal Source Render Plan

These cases define the language-neutral rendering boundary between semantic
merge decisions and source output.

Providers produce ordered fragments. The shared renderer copies exact source
lines, inserts explicitly synthesized fragments, and localizes conflict markers
without parsing or inferring syntax.
