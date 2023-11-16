# PyPageCache

## Introduction

Welcome to PyPageCache, a tool designed to help you manage and understand disk page caching in your Python applications. 

Whether you're working on a data-intensive application or building a database, PyPageCache provides insights into how your code interacts with the disk and OS page cache.

## Installation

You can install PyPageCache using pip:

```bash
pip install pypagecache
```

## Getting Started

### View how many pages are in cache
To start using PyPageCache, import the module and create an instance by specifying the path to the file or directory you want to monitor:

```python
from pypagecache import PyPageCache

cache_stats = PyPageCache("/path/to/your/file_or_directory").stats()
print(cache_stats)
```
This should print something like this:
```text
=> Page cache stats: [14359/14359] (100.0%)
```
This indicates that this directory/file contains 14359 pages and all of it are in page cache.


### Warming the cache
Want to reduce the page faults in your app by prewarming the page cache? 
Simply touch all files you care about. 
```python
PyPageCache("/path/to/files").evict()
```
Obviously caching beyond your physical memory limits will result in eviction of older pages. 


### Evicting file pages from cache
Let's say you want to start afresh and see how your app performs when there are no data pages lying in your page cache. You can evict your data files & perform the test.

```python
PyPageCache("/path/to/files").evict()
```
Obviously caching beyond your physical memory limits will result in eviction of older pages. 


## Recipes

Now that we know what are the basic operations that we can leverage. Let's do something more interesting.
Let's see if we can include this as part of our specs.

### Testing Cached pages by your app
```python
import unittest
from pypagecache import PyPageCache

class TestPyPageCache(unittest.TestCase):

    def setUp(self):
        # Set up PyPageCache for a specific file
        self.test_file_path = "/path/to/test/file.txt"
        self.ppc = PyPageCache(self.test_file_path)

        # Perform cache eviction to ensure a clean slate
        self.ppc.evict()

    def tearDown(self):
        # Clean up resources if needed
        pass
    
    def my_io_intensive_function(self):
        # Execute code that performs disk I/O on the specified file
        with open(self.test_file_path, 'r') as file:
            # Read the first 5 lines from the file
            return '\n'.join(file.readline() for _ in range(5))


    def test_disk_io_impact(self):
        # replace this with something that you care about
        self.my_io_intensive_function()
        
        # Retrieve and analyze page cache statistics
        stats = self.ppc.stats()
        print(f"File Size: {stats.filesize} bytes")
        print(f"Page Size: {stats.pagesize} bytes")
        print(f"Cached Pages: {stats.cached_pages}")
        print(f"Total Pages: {stats.total_pages}")

        # Add your assertions based on the obtained statistics
        self.assertLess(stats.cached_pages, 20, "Cached pages should be under 20 for a data read")
        self.assertLess(stats.cached_percent(), 1.0, 
                        "Cache ratio should be low since we're only reading top 5 lines." + 
                        "It should not require the entire file to be paged")
        self.assertGreaterEqual(stats.cached_pages, 1, "It should atleast read 1 page")

if __name__ == '__main__':
    unittest.main()
```

### Dynamic Cache Monitoring in a Loop
If you want to continuously monitor cache statistics while your application is running, you can incorporate PyPageCache into a loop.

```python
import time
from pypagecache import PyPageCache

file_path = "/path/to/your/file.txt"
ppc = PyPageCache(file_path)

while True:
    cache_stats = ppc.stats()
    print(f"Current cache stats: {cache_stats}")
    time.sleep(60)  # Sleep for 1 minute before checking again
```

## Contributing
First off, thanks for considering contributing to PyPageCache! 👏

PyPageCache is an early project, and I'd love to see it grow with the help of the community. Whether you're a seasoned developer or just starting, there are plenty of ways to contribute. Here's how you can get involved:

- **Bug Reports:** Found a bug? Open an issue on [GitHub](https://github.com/lokeshdevnani/pypagecache/issues). Be sure to provide as much detail as possible to help squash that pesky bug.

- **Feature Requests:** Have an idea for a new feature? Share it! Open an issue and let's discuss how we can make PyPageCache even better.

- **Pull Requests:** Feel free to submit pull requests for bug fixes, enhancements, or new features. I'll review them with a smile (and maybe a virtual high-five 🙌).


## License

PyPageCache is released under the [MIT License](https://opensource.org/licenses/MIT). Feel free to check out the full license for the legal details, but in a nutshell, you're free to use, modify, and distribute PyPageCache as long as you include the original license and disclaimer.

## Acknowledgements
I want to express my gratitude to the [vmtouch](https://hoytech.com/vmtouch/) project, which served as a significant source of inspiration for PyPageCache. Their innovative approach to page caching has been a guiding light for this project.

## Author
Hi there! I'm the lone hacker behind PyPageCache. If you have questions, suggestions, or just want to chat about page caching in Python, feel free to reach out:

- [lokeshdevnani](https://github.com/lokeshdevnani) (Github)
- [lokesh.me](https://lokesh.me) (Blog)

