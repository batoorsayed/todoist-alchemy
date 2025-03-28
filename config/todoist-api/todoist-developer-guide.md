Developing with Todoist

Thanks for your interest in developing apps with Todoist! In this guides section we'll provide an overview of the APIs we offer and cover some common topics for application development using our APIs.

You can use our APIs for free, but depending on your Todoist account plan, some features might be restricted.

If you are looking for reference documentation for our APIs please proceed to either the REST API Reference or Sync API Reference.

Please consider subscribing to the Todoist API mailing list to get important updates.
Our APIs

We offer two APIs for external developers, providing different models for sending and receiving data.
Rest API

The Todoist REST API offers the simplest approach to read and write data on the Todoist web service.

For most common application requirements this is our recommended API for external developers and uses an approach that should be familiar for anyone with experience calling RESTful APIs.

We've provided a Getting Started tutorial section within our REST API documentation to introduce you to the API and some common flows you'll encounter when developing Todoist applications. If you are totally new to our APIs or even unfamiliar with Todoist this is a great place to start.
Sync API

The Todoist Sync API is used by our web and mobile applications and is recommended for clients that will maintain a local representation of a user's full account data. It allows for incrementally sending and receiving account data by identifying positions in an account's state history using a sync token.

This API also contains additional endpoints for areas like account management and less common features that may not yet be implemented on the newer REST API.

Within the documentation for the Sync API you'll also find a Getting Started tutorial that will introduce you to using the Sync endpoint to send and receive data.
Our SDKs

Our Python and JavaScript Client SDKs simplify working with Todoist data by reducing the complexity of calling the Todoist APIs.

They are based on the Todoist REST API, are easily installable from the most popular package registries, and you can view examples of their usage in our documentation's examples section.
Integration Archetypes

You can leverage our APIs in countless ways. In this section, we'll introduce a few typical examples of integrations built on top of our APIs:

    Easily create tasks in Todoist within your app. By leveraging our Quick Add endpoint, enable your users to quickly add new tasks to Todoist via our natural language syntax. By automatically appending links to your app to the task content, you can help your users find content within your app faster and return more frequently. The Quick Add endpoint is the quickest way to get started with Todoist API!
    Enrich Todoist tasks in your app. Are you building an app that helps people organize their life or work? Tap into your users' existing Todoist tasks and enable them to focus on a single Todoist task at a time or visually organize their day. To build these scenarios, start by getting all of your user's active tasks.
    Sync Todoist data with your app. Be it two-way sync with Outlook or building powerful automation workflows, our Sync API is purpose-built for heavy-duty syncing.

Designing browser extensions
Introduction

If you chose to build a browser extension that injects functionality to the Todoist web app, please read through the following guidelines to ensure the best experience for your users.

Browser extensions can integrate into Todoist within the task list and task view.
Task view extensions

When adding UIs inside the Task view through a browser extension, consider the following:

    Browser extensions live in the sidebar,
    Make sure the extension is compatible with the Mini view of Todoist (when browser width is reduced to a smaller size, the task view design removes the sidebar and stacks task attributes). Here, your extension should display an icon that represents your extension similar to the task attributes.
    In the Mini view, place integrated extensions above sub-tasks

Example

As an example, to demonstrate the guidelines above, we designed a mock Timer extension.

    The extension is on the last position within the Task view sidebar.
    The extension’s name is above the extension’s custom UI.
    In the Mini view, the extension uses an icon instead of name to represent its identity.
    In the Mini view, the extension UI is next to the extension icon, following the layout of other Todoist task attributes.

Designing UI Extensions

UI Extensions are modules that can be added to an integration to extend the Todoist UI with additional functionality.

Learn more about this in the dedicated UI Extensions section.
Authorization

In order to make authorized calls to the Todoist REST or Sync APIs, your application must first obtain an access token.

The following section describes the process for using the OAuth protocol to obtain an access token from the user.
OAuth

External applications can obtain a user authorized API token via the OAuth2 protocol. Before getting started, developers need to create their applications in the App Management Console and configure a valid OAuth redirect URL. A registered Todoist application is assigned a unique Client ID and Client Secret which are needed for the OAuth2 flow.

This procedure is comprised of 3 steps.
Step 1: Authorization request

    An example of the URL to the authorization endpoint:

https://todoist.com/oauth/authorize?client_id=0123456789abcdef&scope=data:read,data:delete&state=secretstring

Redirect users to the authorization URL at the endpoint https://todoist.com/oauth/authorize, with the specified request parameters.
Required parameters
Name 	Description
client_id
String
	The unique Client ID of the Todoist application that you registered.
scope
String
	A comma separated list of permissions that you would like the users to grant to your application. See the below table for detail on the available scopes.
state
String
	A unique and unguessable string. It is used to protect you against cross-site request forgery attacks.
Permission scopes
Name 	Description
task:add 	Grants permission to add new tasks (the application cannot read or modify any existing data).
data:read 	Grants read-only access to application data, including tasks, projects, labels, and filters.
data:read_write 	Grants read and write access to application data, including tasks, projects, labels, and filters. This scope includes task:add and data:read scopes.
data:delete 	Grants permission to delete application data, including tasks, labels, and filters.
project:delete 	Grants permission to delete projects.
Potential errors
Error 	Description
User Rejected Authorization Request 	When the user denies your authorization request, Todoist will redirect the user to the configured redirect URI with the error parameter: http://example.com?error=access_denied.
Redirect URI Not Configured 	This JSON error will be returned to the requester (your user's browser) if redirect URI is not configured in the App Management Console.
Invalid Application Status 	When your application exceeds the maximum token limit or when your application is being suspended due to abuse, Todoist will redirect the user to the configured redirect URI with the error parameter: http://example.com?error=invalid_application_status.
Invalid Scope 	When the scope parameter is invalid, Todoist will redirect the user to the configured redirect URI with error parameter: http://example.com?error=invalid_scope.
Step 2: Redirection to your application site

When the user grants your authorization request, the user will be redirected to the redirect URL configured for your application. The redirect request will come with two query parameters attached: code and state.

The code parameter contains the authorization code that you will use to exchange for an access token. The state parameter should match the state parameter that you supplied in the previous step. If the state is unmatched, your request has been compromised by other parties, and the process should be aborted.
Step 3: Token exchange

    An example of exchanging the token:

$ curl "https://todoist.com/oauth/access_token" \
    -d "client_id=0123456789abcdef" \
    -d "client_secret=secret" \
    -d "code=abcdef" \
    -d "redirect_uri=https://example.com"

    On success, Todoist returns HTTP 200 with token in JSON object format:

{
  "access_token": "0123456789abcdef0123456789abcdef01234567",
  "token_type": "Bearer"
}

Once you have the authorization code, you can exchange it for the access token by sending a POST request to the following endpoint:

https://todoist.com/oauth/access_token.
Required parameters
Name 	Description
client_id
String
	The Client ID of the Todoist application that you registered.
client_secret
String
	The Client Secret of the Todoist application that you registered.
code
String
	The code that was sent in the query string to the redirect URL in the previous step.
Potential errors
Error 	Description
Bad Authorization Code Error 	Occurs when the code parameter does not match the code that is given in the redirect request: {"error": "bad_authorization_code"}
Incorrect Client Credentials Error 	Occurs when the client_id or client_secret parameters are incorrect: {"error": "incorrect_application_credentials"}
Colors

Some objects (like projects, labels, and filters) returned by our APIs may have colors defined by an id or name. The table below shows all information you may need for any of these colors.
ID 	Name 	Hexadecimal 		ID 	Name 	Hexadecimal
30 	berry_red 	#B8255F 		40 	light_blue 	#6988A4
31 	red 	#DC4C3E 		41 	blue 	#4180FF
32 	orange 	#C77100 		42 	grape 	#692EC2
33 	yellow 	#B29104 		43 	violet 	#CA3FEE
34 	olive_green 	#949C31 		44 	lavender 	#A4698C
35 	lime_green 	#65A33A 		45 	magenta 	#E05095
36 	green 	#369307 		46 	salmon 	#C9766F
37 	mint_green 	#42A393 		47 	charcoal 	#808080
38 	teal 	#148FAD 		48 	grey 	#999999
39 	sky_blue 	#319DC0 		49 	taupe 	#8F7A69
Mobile app URL schemes

Our applications for Android and iOS support custom URL schemes for launching to specific views and initiating some common actions.
Views

The following schemes are available to open a specific view:
Scheme 	Description
todoist:// 	Opens Todoist to the user's default view.
todoist://today 	Opens the today view.
todoist://upcoming 	Opens the Upcoming view.
todoist://profile 	Opens the profile view.
todoist://inbox 	Opens the inbox view.
todoist://teaminbox 	Opens the team inbox view. If the user doesn't have a business account it will show an alert and redirect automatically to the inbox view.
todoist://notifications 	Opens notifications view.
Tasks

    Example of adding a task:

todoist://addtask?content=mytask&date=tomorrow&priority=4

    Here's an example of a content value:

Create document about URL Schemes!

    And how it should be supplied using Percent-encoding:

Create&20document%20about%20URL%20Schemes%21

    Here's an example of a date value:

Tomorrow @ 14:00

    And how it should be supplied using Percent-encoding:

Tomorrow%20@%2014:00

The following schemes are available for tasks:
Scheme 	Description
todoist://task?id={id} 	Opens a task by ID.
todoist://addtask 	Opens the add task view to add a new task to Todoist.

The todoist://addtask scheme accepts the following optional values:
Value 	Description
content
URL encoding
	The content of the task, which should be a string that is in Percent-encoding (also known as URL encoding).
date
URL encoding
	The due date of the task, which should be a string that is in Percent-encoding (also known as URL encoding). Look at our reference to see which formats are supported.
priority
Integer
	The priority of the task (a number between 1 and 4, 4 for very urgent and 1 for natural).
Note: Keep in mind that very urgent is the priority 1 on clients. So, p1 will return 4 in the API.

This URL scheme will not automatically submit the task to Todoist, it will just open and pre-fill the add task view. If no values are passed, the add task view will just be opened.
Projects

The following schemes are available for tasks:
Scheme 	Description
todoist://projects 	Opens the projects view (shows all projects).
todoist://project?id={id} 	Opens a specific project by ID.

    Example of opening a specific project:

todoist://project?id=128501470

The todoist://project scheme accepts the following required value:
Value 	Description
id
Integer
	The ID of the project to view. If the ID doesn't exist, you don't have access to the project, or the value is empty, an alert will be showed and the user will be redirected to the projects view.
Labels

The following schemes are available for labels:
Scheme 	Description
todoist://labels 	Opens the labels view (shows all labels)
todoist://label?name={name} 	Opens a specific label by name.

    Example of opening a specific label:

todoist://label?name=Urgent

The todoist://label scheme accepts the following required value:
Value 	Description
name
String
	The name of the label to view. If the label doesn't exist, you don't have access to the label, or the value is empty, an alert will be shown.
Filters

The following schemes are available for filters:
Scheme 	Description
todoist://filters 	Opens the filters view (shows all filters)
todoist://filter?id={id} 	Opens a specific filter by ID.

    Example of opening a specific filter:

todoist://filter?id=9

The todoist://filter scheme accepts the following required value:
Value 	Description
id
Integer
	The ID of the filter to view. If the ID doesn't exist, you don’t have access to the filter, or the value is empty, an alert will be showed and the user will be redirected to the filters view.
Search

The following scheme is available for searching (Android only):
Scheme 	Description
todoist://search?query={query} 	Used to search in the Todoist application.

    Example of searching for "Test & Today":

todoist://search?query=Test%20%26%20Today

The todoist://search scheme accepts the following required value:
Value 	Description
query
URL encoding
	The query to search in the Todoist application, which should be a string that is in Percent-encoding (also known as URL encoding).
Desktop app URL schemes

Our Desktop applications support custom URL schemes for launching to specific views and initiating some common actions. This can be useful for integrating Todoist with other applications or services, as browsers and other applications can open these URLs to interact with Todoist. As an example, you could create a link in your application that opens a specific project in Todoist, or a link that adds a task to Todoist.
Views

The following schemes are available to open a specific view:
Scheme 	Description 	minimum version requirement
todoist:// 	Opens Todoist. 	9.2.0
todoist://inbox 	Opens the inbox view. 	9.2.0
todoist://today 	Opens the today view. 	9.2.0
todoist://upcoming 	Opens the Upcoming view. 	9.2.0
todoist://project?id={id} 	Opens the project detail view for a given project ID. 	9.2.0
todoist://task?id={id} 	Opens the task detail view for a given task ID. 	9.2.0
todoist://notifications 	Opens the notifications view. 	9.10.0
todoist://filters-labels 	Opens the filters & labels view. 	9.10.0
todoist://filter?id={id} 	Opens the filter view for a given filter ID. 	9.10.0
todoist://label?id={id} 	Opens the label view for a given label ID. 	9.10.0
todoist://search?query={query} 	Opens the search view for the specified query. 	9.10.0
todoist://projects 	Opens my projects view. 	9.10.0
todoist://projects?workspaceId={id} 	Opens the projects view for the given workspace ID. 	9.10.0
todoist://templates 	Opens the templates view. 	9.10.0
todoist://templates?id={id} 	Opens the template view for the given template ID. 	9.10.0
Tasks

    Example of adding a task:

Note that this will not add the task but open the Global Quick Add refilled with given values.

todoist://openquickadd?content=mytask&description=%20is%20a%20description

The following schemes are available for tasks:
Scheme 	Description
todoist://task?id={id} 	Opens a task by ID.
todoist://openquickadd 	Opens the global quick add to add a new task to Todoist.

The todoist://openquickadd scheme accepts the following optional values:
Value 	Description
content
URL encoding
	The content of the task, which should be a string that is in Percent-encoding (also known as URL encoding).
description
URL encoding
	The content of the task, which should be a string that is in Percent-encoding (also known as URL encoding).

This URL scheme will not automatically submit the task to Todoist, it will just open and pre-fill the global quick add panel. If no values are passed, the global quick add will just be open.
Projects

The following schemes are available for tasks:
Scheme 	Description
todoist://project?id={id} 	Opens a specific project by ID.

    Example of opening a specific project:

todoist://project?id=128501470

The todoist://project scheme accepts the following required value:
Value 	Description
id
Integer
	The ID of the project to view. If the ID doesn't exist it will just open Todoist. If you don't have access to the project, or the project does not exist, an error message will be shown to the user.
Marketing your app

After you complete the work on your Todoist integration, you can choose to submit it for certification.

If your app passes the certification process, we will create a dedicated page on our Integrations Pages to showcase your work, and help with marketing the integration.

Certifying your integration means:

    Creating a submission
    Passing certification
    Getting published
    After publishing

Submitting your app for certification is optional and primarily serves to give your integration more visibility. Certification is not required to develop with the Todoist APIs and share the resulting integration with users.
Creating a submission

First, fill out the app submissions form. Just add a marketing description, installation instructions, and links to your website and privacy policy.

We'll also ask you for some images, in the following format:

    Your app icon, in JPG format on a white background. The size of the image should be 250x250px.
    One or more screenshots in JPG format at 1600x1000px. If your screenshot includes images of Todoist, it should use the default theme (Red).

Passing certification

After you've submitted your app, we'll email you a confirmation. We aim to review submissions and respond with any feedback within ten business days.
Certification process

The certification is composed of:

    Submission review - Ensuring that the data you submitted to the form will create a solid integration page. You can expect feedback about, e.g., the length of texts you submitted or opportunities to improve the screenshots.
    Technical review - We will manually test the integration to see if it works as described and that there are no critical bugs that prevent users from using the integration to the fullest.
    Marketing review - Even though our Integration Pages represent the work of our partners, we still aim to present integrations consistently and might give feedback on, e.g., the voice of descriptions. We will suggest concrete changes to make the process easier for you where possible.

If we find any issues along the way, we'll be in touch via email and work with you to resolve them. If you have any questions or updates at any time, you can reply to any of the emails you've received during the submissions process. We'll aim to get back to you within two business days.
Certification requirements

Below is a list we frequently focus on during review. Note that meeting the below criteria is does not guarantee passing the certification but is broadly representative of the criteria we look at.

    All the fields in the submission form are filled out in English.
    Your app complements or enhances the functionality of Todoist. It should not replicate functionality already included.
    Your app is free of any functional errors during our testing.
    Your app integrates with Todoist directly. We do not host listings for services that integrate solely via 3rd party automation providers like IFTTT and Zapier, or integrations that rely solely on our email forwarding feature.
    Users can easily set up the integration using the instructions you've provided.
    All links provided are HTTPS enabled to ensure the security of our users. If you're submitting a native platform app, it must be signed with a trusted certificate.
    Any use of the Todoist name or logo follows our brand guidelines.
    Your privacy policy ensures you will not sell or share our users' data with any third parties without their consent.
    The marketing descriptions and images you've provided are clear, follow our style and the guidelines in the integration submission form.

Getting published

Once your submission has passed our review, we'll publish your listing and provide you with a public link that you can share! We'll also translate your listing to expand your marketing reach where it makes sense for your app.
After publishing

After we publish your integration page, please do reach out to us in the following cases:

    You update your integration after launch. We will highlight the update with an Updated tag.
    Interest in more comprehensive marketing collaboration.

If you have any further questions or updates to provide after we've published your integration page, you can always reach out to our app submissions team at https://todoist.com/contact by selecting the following categories (in order of appearance): Something else → Integrations Development.

We're happy to help!
Brand usage

Thanks for using Todoist's APIs to build an application!

If you plan to utilize Todoist's logo or branding in the visual design of your application or website, please adhere to Todoist's brand guidelines.

In addition, please take note of the following:

    "Todoist" should not be the first word in your application's name. It may be used elsewhere in the name, though. For instance "x for Todoist" or "x with Todoist", etc. This makes it clear that your application is created by you and not by Doist.
    You must clearly state that your application is "not created by, affiliated with, or supported by Doist" in your application description.

By using the Todoist marks you agree to properly follow the above brand guidelines as well as our Terms of Service. For further information about the use of the Todoist brand, please contact press@doist.com.
Get in touch

Interested in developing an integration for Todoist but unsure where to start? Get in touch with our support team, and we'll be happy to help.