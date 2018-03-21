# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

# stdlib
import os
import logging
import datetime
import importlib
import argparse
import inspect
import pkgutil

# external
from mixbox import entities
from mixbox.vendor.six import itervalues, iteritems, iterkeys

__version__ = "0.6"

# Module-level logger
LOG = logging.getLogger(__name__)

# ----------------- CLASS DEFINITION -----------------


class ModelMapper(object):
    """The ModelMapper script is not an essential part of the stixmarx library.
     It serves as a complimentary tool that helps automating the creation of
     mappings from the Python Object Model (python-stix, python-cybox,
     python-maec, etc.) that contain the new mixbox changes to XML constructs
     (Element, @attribute or text()). It can be used in any other library
     that implements TypeFields from the mixbox library.

     The generated content is found under stixmarx/fields/ directory.
    """
    def __init__(self, *args):
        self._MAP_PACKAGES = args
        self._FIELDS = {}
        self._VERSIONS = {}
        self._IMPORTS = set()
        self.initialize_mappings()

    def initialize_mappings(self):
        for module_name in self._MAP_PACKAGES:
            imported_module = self._get_module(module_name)
            self._VERSIONS[imported_module.__name__] = imported_module.__version__

            objects = self._get_class_instances(modulename(imported_module), imported_module)
            self._manage_module_objects(objects)

    def _manage_module_objects(self, objects):
        for obj in objects:
            self._parse(obj)

    def _parse(self, object_):
        content = {}
        key = fully_qualified_name(object_)
        import_str = module(object_)

        for properties in object_.typed_fields_with_attrnames():
            attr_name, typed_field = properties
            tf = handle_typefield(typed_field)

            if tf:
                content[attr_name] = tf

        if content:
            self._FIELDS[key] = content
            self._IMPORTS.add(import_str)

    @staticmethod
    def _get_module(module_name):
        """Returns a tuple with all objects that could be instantiated
        without arguments.

        Args:
            module_name: A string object. It represents the name of the top-level module.

        Returns:
            A ModuleType object with all sub-modules imported from the given module.
        """
        top_level_module = importlib.import_module(module_name)

        prefix = modulename(top_level_module) + "."

        try:
            for module_loader, name, is_pkg in pkgutil.walk_packages(path=top_level_module.__path__, prefix=prefix):
                importlib.import_module(name, top_level_module)
        except (ImportError, ImportWarning) as e:
            LOG.debug(str(e))

        return top_level_module

    def _get_class_instances(self, module_name, module):
        """Returns a tuple with objects that could be instantiated
        without arguments.

        Args:
            module: A ModuleType object. It can be either in the lowest or
            highest level module.

        Returns:
            A tuple with `mixbox.Entity` objects from the given module.
        """
        result = ()

        for klass_ in itervalues(vars(module)):
            try:
                if inspect.isclass(klass_) and issubclass(klass_, entities.Entity):
                    result += (klass_(),)
                elif inspect.ismodule(klass_) and (module_name in modulename(klass_) and module_name != modulename(klass_)):
                    result += self._get_class_instances(module_name, klass_)
            except:
                msg = "{0} could not be instantiated without args."
                LOG.info(msg.format(klass_))
                continue

        return result

    def to_file(self):
        """
        Writes content of mapping dictionary to file.

        *Note:
            The output file directory and filename will be
                {Drive}:{PATH}/Desktop/fields.py
        """
        path = os.path.expanduser("~/Desktop")
        destination = os.path.abspath(path + "/fields.py")

        with open(destination, "w") as outfile:
            outfile_header(outfile, self._VERSIONS)
            outfile_fields_header(outfile)

            for key in sorted(iterkeys(self._FIELDS)):
                outfile.write(" " * 4)
                outfile.write("\"{0}\": {{\n".format(key))

                for in_key, in_val in sorted(iteritems(self._FIELDS[key])):
                    outfile.write(" " * 8)
                    outfile.write("\"{0}\": \"{1}\",\n".format(in_key, in_val))

                outfile.write(" " * 4)
                outfile.write("},\n")

            outfile.write("}\n")


# ----------------- UTILITIES -----------------


def outfile_header(outfile, versions):
    today = datetime.datetime.now()
    ver_str = str()

    for k, v in iteritems(versions):
        ver_str += "# {mod}\t-\t{ver}\n".format(mod=k, ver=v)

    outfile.write(
        "# Copyright (c) {year}, The MITRE Corporation. All rights reserved.\n"
        "# See LICENSE.txt for complete terms.\n\n"
        "# This is an auto-generated file.\n"
        "{versions}\n"
        "__date__ = \"{datetime}\"\n\n".format(year=today.year,
                                               versions=ver_str,
                                               datetime=today)
    )


def outfile_fields_header(outfile):
    outfile.write(
        "\n# Maps Python instance attribute names to XML instance field names for\n"
        "# Python API classes.\n"
        "_FIELDS = {\n"
    )


def fully_qualified_name(object_):
    return module(object_) + "." + classname(object_)


def module(object_):
    return object_.__module__


def modulename(module_):
    return str(module_.__name__)


def classname(object_):
    return object_.__class__.__name__


def handle_typefield(tf):
    if tf.name[0].islower() and tf.type_ is None:

        if tf.name == "classxx":
            return "@{0}".format(tf.key_name)

        elif tf.name == "valueOf_":
            return "text()"

        elif tf.name == "xsi_type":
            return None

        elif tf.name == "type_":
            return "@type"

        return "@{0}".format(tf.name)

    return tf.name


#  ----------------- MAIN SCRIPT  -----------------


def init_logging(level=logging.DEBUG):
    """Initialize Python logging.
        Args:
            level (int): Specifies the logging level."""
    fmt = "[%(asctime)s] [%(levelname)s] %(message)s"
    logging.basicConfig(level=level, format=fmt)


def _get_argparser():
    """Create and return an ArgumentParser for this application."""
    desc = "model-mapper v{0}".format(__version__)
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument(
        "--log-level",
        default="DEBUG",
        help="The logging output level.",
        choices=["DEBUG", "INFO", "WARN", "ERROR"]
    )

    parser.add_argument(
        "parse",
        default="",
        help="The name of the library to perform the mappings. (e.g. stix)"
    )

    return parser


def main():
    # Parse the commandline args
    parser = _get_argparser()
    args = parser.parse_args()

    # Initialize logging
    init_logging(args.log_level)

    try:
        mapper = ModelMapper(args.parse)
        mapper.to_file()
    except Exception as ex:
        LOG.exception(ex)


if __name__ == "__main__":
    main()
