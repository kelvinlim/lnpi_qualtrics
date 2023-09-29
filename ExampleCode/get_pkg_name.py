import pkgutil

package_name = 'decoders'
package = __import__(package_name)
module_names = [name for _, name, _ in pkgutil.walk_packages(package.__path__)]

for module_name in module_names:
    print(module_name)
    