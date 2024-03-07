# Nestor Workflow Through User Interface

Nestor is a toolkit to enable  improved user-centric workflows in NLP, specifically for kick-starting annotation and information modelling. 
How this got implemented has morphed significantly over time, as we realized how crucial consistent iteration on existing annotations was, and how powerful constant feedback from the supporting algorithms could be. 

## Programmatic 
Nestor originally began as a set of prototype transformers on top of the well-known scikit-learn pipeline paradigm. 
This has been updated and maintained over time, to make use of nestor outputs within NLP pipelines in the wild. 

For examples of using nestor this way, see our [Examples](examples) page

## Graphical (GUI)
Many of the Nestor-associated tasks are better approached through a GUI. 

There have been several graphical interfaces under development:

[`nestor-qt`](https://github.com/usnistgov/nestor-qt)
:    legacy desktop-oriented app built using PyQT. His the most development and is more feature-complete. No longer actively developed beyond nestor v0.5, though still maintained for research purposes. 
  
[`nestor-web`](https://github.com/usnistgov/nestor-web)
:   modern interface built on Electron. Intended to showcase a portable, cross-platform proof-of concept. Consequently it is less feature-complete, but looks and feels cleaner. 


More interfaces are planned, possibly as Jupyter widgets or Panel dashboards. 
Please contact us if Nestor-workflow interfaces are of interest!


