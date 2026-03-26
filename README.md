# Reach Concept Development Team

This repository provides a robust Docker-based template for the Reach Concept Development Team. The aim is to streamline and standardize the development workflow, enabling the team to:

- **Run Odoo effortlessly**
- **Debug applications effectively**
- **Write and execute unit tests seamlessly**
- **Create and manage Pull Requests efficiently**

## Features

1. **Pre-configured Docker Environment**
   - Simplifies the setup process with all dependencies ready out-of-the-box.

2. **Integrated Debugging Tools**
   - Provides support for debugging with tools such as `pdb` and external debuggers.

3. **Testing Framework**
   - Comes with a pre-installed unit testing framework to ensure code quality and reliability.

4. **Version Control Integration**
   - Optimized for creating, managing, and testing Pull Requests before merging.

5. **Customizable for Team Needs**
   - Easily adaptable for new requirements or tools.

## Getting Started

Follow these steps to get the template up and running:

### 1. Clone the Repository
```bash
$ git clone <repository-url>
$ cd <repository-directory>

cd odoo
git clone -b 18.0 https://github.com/odoo/odoo.git
git clone -b 18.0 https://github.com/odoo/enterprise.git