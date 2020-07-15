# Short title

Aggregate and query information from web portals

# Long title

Retrieve and visualize relevant information from a collection of web portals with a natural language query

# Author

> Provide names and IBM email addresses.

* Balaji Kadambi <bkadambi@in.ibm.com>
* Manjula G. Hosurmath  <mhosurma@in.ibm.com>

# URLs

### Github repo

* [Aggregate and query information from web portals](https://github.com/IBM/discovery-webcrawl-insights)

# Summary

In this code pattern, we build an application that uses the APIs of IBM Discovery service to create, query, get status and delete a document collection of web portals. The application renders the query results on a custom built web user interface. This provides flexibility to the end-user to design and build the web user interface for specific information and visualization requirements. 

# Technologies

* [Python](https://developer.ibm.com/technologies/python/): An open-source interpreted high-level programming language for general-purpose programming.

# Description

There is a lot of information on the web, and we are always interested in getting the relevant information. The below two common scenarios drive the need for it:
- There is usually a specific item of interest, and we try to get all the relevant infomration about the item.
- We have a question and are searching to find the answers for it that is in the web pages.

In this code pattern, we try to address a specific scenario where we try to query for relevant information from a group of web pages. IBM Discovery service provides the ability to crawl through web pages and build a queryable collection. We will use this feature to build an application using which you can:
- Specify a list of URLs that Discovery will crawl to build the collection.
- Specify a query in natural language and get relevant results with insights from Discovery.
- Visualize the information

When you have completed this code pattern, you will understand how to:
- Use the Discovery APIs -
  - to create a collection using webcrawl.
  - to get the status of a collection.
  - to delete a collection.
  - Parse, read and visualize the results from Discovery.


# Flow
1. User requests for creation/status/deletion of a collection or queries a collection through a custom built web UI.
2. The request is sent to a server application on the cloud.
3. The application invokes an api on the Discovery service using the Watson SDK.
4. The Discovery service processes the results and sends it back to the application. The results are then visualized by the User.


# Instructions

> Find the detailed steps for this pattern in the [readme file](https://github.com/IBM/discovery-webcrawl-insights/blob/master/README.md). The steps will show you how to:

1. Clone the repo
2. Deploy the application
3. Analyze the results

# Components and services

[IBM Discovery](https://www.ibm.com/in-en/cloud/watson-discovery)

# Runtimes

* Python 3


# Related IBM Developer content

> List any IBM Developer resources that are closely related to this pattern, such as other patterns, blog posts, tutorials, etc..

* [Learning Path : Getting started with Watson Discoery](https://developer.ibm.com/technologies/artificial-intelligence/series/learning-path-watson-discovery/)

