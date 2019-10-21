<a name="OpenStack"></a>

## Openstack
OpenStack is a cloud operating system that controls large pools of compute, storage, and networking resources throughout a datacenter, all managed and provisioned through APIs with common authentication mechanisms.
A dashboard is also available, giving administrators control while empowering their users to provision resources through a web interface.
Beyond standard infrastructure-as-a-service functionality, additional components provide orchestration, fault management and service management amongst other services to ensure high availability of user applications.

#### OOO / TripleO
"Openstack on Openstack" nutzt Openstack selber als „undercloud“ um Openstack zu installieren.
TripleO is a project aimed at installing, upgrading and operating OpenStack clouds using OpenStack’s own cloud facilities as the foundation - building on Nova, Ironic, Neutron and Heat to automate cloud management at datacenter scale
#### Nova
Nova is the OpenStack project that provides a way to provision compute instances (aka virtual servers). Nova supports creating virtual machines, baremetal servers (through the use of ironic), and has limited support for system containers. Nova runs as a set of daemons on top of existing Linux servers to provide that service.
It requires the following additional OpenStack services for basic function:
Keystone: This provides identity and authentication for all OpenStack services.
Glance: This provides the compute image repository. All compute instances launch from glance images.
Neutron: This is responsible for provisioning the virtual or physical networks that compute instances connect to on boot.
It can also integrate with other services to include: persistent block storage, encrypted disks, and baremetal compute instances.
#### Swift
Swift ist ein hoch verfügbarer, dezentralisierter, eventually consistent object/blob store. Organizations can use Swift to store lots of data efficiently, safely, and cheaply. It's built for scale and optimized for durability, availability, and concurrency across the entire data set. Swift is ideal for storing unstructured data that can grow without bound.
#### Cinder
Cinder is a Block Storage service for OpenStack. It virtualizes the management of block storage devices and provides end users with a self service API to request and consume those resources without requiring any knowledge of where their storage is actually deployed or on what type of device. This is done through the use of either a reference implementation (LVM) or plugin drivers for other storage.
#### Neutron
ist ein SDN networking Projekt um networking-as-a-service (NaaS) in virtuellen compute environments zur Verfügung zu stellen. Wird von uns mit Contrail ersetzt.
#### Keystone
Keystone ist der Identity Service von OpenStack. Er stellt API client authentication, service discovery,
und distributed multi-tenant authorization durch Implementierung der OpenStack Identity API. 
Unterstützt LDAP, OAuth, OpenID Connect, SAML and SQL.
#### Heat
Heat is the main project in the OpenStack Orchestration program. It implements an orchestration engine to launch multiple composite cloud applications based on templates in the form of text files that can be treated like code. A native Heat template format is evolving, but Heat also endeavours to provide compatibility with the AWS CloudFormation template format, so that many existing CloudFormation templates can be launched on OpenStack. Heat provides both an OpenStack-native ReST API and a CloudFormation-compatible Query API.
#### Horizon
Horizon ist die canonical Implementation von OpenStack's dashboard, bietet eine web based GUI zu OpenStack services.


#### Kolla
Kolla provides production-ready containers and deployment tools for operating <a href="#OpenStack">OpenStack</a> clouds that are scalable, fast, reliable, and upgradable using community best practices. 

https://wiki.openstack.org/wiki/Kolla


#### Infrastructure as code
Infrastructure as code (IaC) is the process of managing and provisioning computer data centers through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools.

   * <a href="#Ansible">Ansible</a>
   * <a href="#Chef">Chef</a>
   * <a href="#Puppet">Puppet</a>
   * <a href="#Salt">Salt</a>
   * <a href="#Terraform">Terraform</a>

https://en.wikipedia.org/wiki/Infrastructure_as_code

<a name="Ansible"></a>

#### Ansible
Ansible is an open-source software provisioning, configuration management, and application-deployment tool.

https://en.wikipedia.org/wiki/Ansible_(software)

<a name="Chef"></a>

#### Chef
Chef is a company and the name of a configuration management tool written in Ruby and Erlang.

https://en.wikipedia.org/wiki/Chef_(software)

<a name="Puppet"></a>

#### Puppet
Puppet is an open-core software configuration management tool.

https://en.wikipedia.org/wiki/Puppet_(company)#Puppet

<a name="Salt"></a>

#### Salt
Salt (sometimes referred to as SaltStack) is Python-based, open-source software for event-driven IT automation, remote task execution, and configuration management. 

https://en.wikipedia.org/wiki/Salt_(software)

<a name="Terraform"></a>

#### Terraform
Terraform is an open-source infrastructure as code software tool created by HashiCorp.

https://en.wikipedia.org/wiki/Terraform_(software)


#### Rancher
Rancher is an open source project that provides a <a href="#Container">container</a> management platform built for organizations that deploy containers in production. 

https://github.com/rancher/rancher


#### Ironic
An <a href="#OpenStack">OpenStack</a> Bare Metal Provisioning Program

https://wiki.openstack.org/wiki/Ironic

#### Glance
Glance provides a service in an <a href="#OpenStack">openStack</a> environment where users can upload and discover data assets that are meant to be used with other services. 

https://docs.openstack.org/glance/latest/

#### Kubernetes
Kubernetes is an open-source container-orchestration system for automating application deployment, scaling, and management

https://en.wikipedia.org/wiki/Kubernetes

<a name="Kubernetes"></a>

#### Helm
Helm is a tool for managing <a href="#Kubernetes">Kubernetes</a> charts.

https://github.com/helm/helm

<a name="Container"></a>

#### Container
A container is a standard unit of software that packages up code and all its dependencies so the application runs quickly and reliably from one computing environment to another. 

https://en.wikipedia.org/wiki/OS-level_virtualization

<a name="Docker"></a>

#### Docker
Docker is a set of platform-as-a-service (PaaS) products that use OS-level virtualization to deliver software in packages called <a href="#Container">containers</a>.

https://en.wikipedia.org/wiki/Docker_(software)

#### Docker Swarm
Docker Swarm is a clustering and scheduling tool for <a href="#Docker">Docker</a> containers.

https://docs.docker.com/engine/swarm/

#### LXC / LXD
LXC—short for “Linux <a href="#Container">Containers</a>, is a solution for virtualizing software at the operating system level within the Linux kernel. 
LXD is an extension of LXC

https://www.sumologic.com/blog/lxc-lxd-linux-containers/

#### IOPS
Input/output operations per second (IOPS) is an input/output performance measurement used to characterize computer storage devices 

https://en.wikipedia.org/wiki/IOPS

#### Microservice
Microservices are a software development technique—a variant of the service-oriented architecture (SOA) architectural style that structures an application as a collection of loosely coupled services.

https://en.wikipedia.org/wiki/Microservices

#### Consul
Consul is a tool for service discovery and configuration. 

https://github.com/hashicorp/consul

#### Linux Namespaces
#### RabbitMQ
#### Openflow
#### Contrail
#### Galera
#### Zookeeper
#### CassandraDB
#### Cumulus
#### Ceph
Verteilte Storage Plattform mit RADOS
#### Quobyte
#### MariaDB

