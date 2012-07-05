# Render model graphs automagically
####################################
#
# If Graphviz is installed, rendering model graphs is fully automated::
#
#     make
#
# On a Mac, the graphs can also be automatically displayed by running::
#
#     make open_graphs
#
# Which apps are graphed and the way they are grouped can be condigured in `model_graphs/Makefile`.

PROJECT_ROOT = ../..
PYTHON = ${PROJECT_ROOT}/env/bin/python

GRAPH_DIR = model_graphs
MAKEGRAPH = ${PYTHON} ${PROJECT_ROOT}/manage.py graph_models -e -g
DOTRENDER = dot
VERSION = $(shell git rev-parse HEAD | head -c 5)
DATE = $(shell date)

all: model_graphs

# Shortcut for render_graphs, cleaning beforehand
model_graphs: clean render_graphs

# Render PDF files
render_graphs: projects.pdf members_organizations.pdf tasks.pdf donations_payments.pdf tasks.pdf misc.pdf

# Open the graphs on a mac
open_graphs: render_graphs
	open *.pdf

# Specific commands to yield specific graphs, so we can do manual grouping
projects.dot:
	${MAKEGRAPH} projects > $@

members_organizations.dot:
	${MAKEGRAPH} members organizations > $@

tasks.dot:
	${MAKEGRAPH} tasks > $@

donations_payments.dot:
	${MAKEGRAPH} payments consolidations donations vouchers > $@

misc.dot:
	${MAKEGRAPH} actions system albums cms events news filemanager weblog > $@

# Generic rule for rendering PDF files out of a .dot
%.pdf: %.dot
	# Make sure we add a version and date tag in there
	${DOTRENDER} -Glabel='$@ - latest commit ${VERSION} - ${DATE}' $< -Tpdf > $@

clean:
	rm -f *.dot *.pdf