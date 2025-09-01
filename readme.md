# Ansible Collection - laurobmb.statusinvest

Documentation for the collection.

### Galaxy collection build
> ansible-galaxy collection build
### Galaxy collection install from file
> ansible-galaxy collection install laurobmb-statusinvest-1.0.0.tar.gz
### Galaxy collection install from git
> ansible-galaxy collection install git+https://github.com/laurobmb/ansible_statusinvest_collection.git,main

> ansible-galaxy collection install laurobmb-statusinvest-1.0.4.tar.gz -p collections/

### Playbook sample using role
    ---
    - name: STATUSINVEST
      hosts: localhost
      tasks:
        - name: Usando a role da collection
          ansible.builtin.import_role:
            name: laurobmb.statusinvest.getdata
          vars:
            acoes: 'petr4'
            fundos: 'hgre11'
          register: greeting

        - name: Debug role
          ansible.builtin.debug:
            msg: "{{ greeting }}"

### Playbook sample using plugin
    ---
    - name: STATUSINVEST
      hosts: localhost
      tasks:
        - name: Usando o modulo diretamente
          laurobmb.statusinvest.statusinvest:
            statusinvest_acoes: "{{ acoes }}"
            statusinvest_fundos: "{{ fundos }}"
          register: greeting
          vars:
            acoes: 'bbas3'
            fundos: 'vghf11'

        - name: Debug modulo
          ansible.builtin.debug:
            msg: "{{ greeting }}"
