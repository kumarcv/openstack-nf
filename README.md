openstack-nf
============

openstack Network Function Virtualization

**Network Service APIs - Version 1.2**
=======================


### - Ravi Chunduru 

Contributiors
=============
### Balaji - Freescale
### Srini Addepalli - Freescale


##1.0  Network Service Appliance Category API


Network Service appliance category API can be used to manage different categories of network service appliances. 



#####1.1  List Network service Appliance Categories


<table cellspacing = 30  >
    <tr>
    <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>GET </td><td> /nsappliances/category </td><td> List all network service Appliance Categories</td>
    </tr>
</table>

Normal Response Code(s): 200, 203

Error Response Codes(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413)

Example JSON response

    {
        "nsappliance-categories": 
        [
            {
                "id": "52415800-8b69-11e0-9b19-734f6af67565",
                "category": "firewall",
                "description": "Firewall Security appliance",
                "shared":True
            },
            {
                "id": "493454534-8b69-11e0-9b19-74f6af672345",
                "category": "IPS",
                "description": "Intrusion Prevention Appliance",
                "shared":False  
            }
        ]
    }




#####1.2  create a Network service category



<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>POST </td><td>/nsappliances/category </td><td> Create a network service Appliance</td>
    </tr> 
</table>

Normal Response Code(s): 202

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404), badMediaType (415), serverCapacityUnavailable (503)

This operation creates a network service category. Each category is identified by UUID.

The following table describes the required and optional attributes that you can specify in the request body.

<table cellspacing = 30  >
    <tr>
        <th>Name</th><th>Description</th><th>Required</th>
    </tr>
    <tr>
        <td>category</td><td>Type of network service Appliance grouped as category. Following are few categories firewall, IPS, WAF etc., User can create category of his choice </td><td>Yes</td>
    </tr>
    <tr>
        <td>description</td><td>Describe about the category</td><td>False</td>
    </tr>
        <tr>
        <td>shared</td><td>Set the accessibility of the nsappliance category for other tenants</td>
    </tr>
</table>

*Network service Appliance Category create JSON request*


    {
        "category": "firewall",
        "description": "Firewall Security appliance",
        "shared":True
    }


*Network service Appliance Category create JSON response*


    {
        "id": "52415800-8b69-11e0-9b19-734f565bc83b",
        "tenant-id": "35415810-6b62-71e0-0b11-234f565bc422",    
        "category": "firewall",
        "description": "Firewall Security appliance",
        "shared":True
    }





#####1.3  Get Network Service Appliance Category Details


<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>GET </td><td>/nsappliances/category/{category_id} </td><td> List details of a specified network service</td>
    </tr>
</table>

Normal Response Code(s): 200, 203

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404)

Specify the Network Service Appliance Category ID as id in the URI.

This operation does not require a request body.

This operation returns the details of a specific Network Service Appliance Category by its ID.

*Example JSON response*


    {
        "id": "52415800-8b69-11e0-9b19-734f565bc83b",
        "tenant-id": "35415810-6b62-71e0-0b11-234f565bc422",
        "category": "firewall",
        "description": "Firewall Security appliance",
        "shared":True
    }






#####1.4  Update a Network Service Appliance Category


<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>PUT </td><td>/nsappliances/category/{category_id} </td><td> Update a specified Network Service Category</td>
    </tr>
</table>

Normal Response Code(s): 200

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404)

This operation enables you to update the editable attributes of a specified Network Service.

Specify the Network Service Appliance Category ID as id in the URI.

The following table describes the attributes that you can specify in the request body:

<table cellspacing = 30  >
    <tr>
        <th>Name</th><th>Description</th>
    </tr>
    <tr>
        <td>description</td><td>You can edit the description of this Network Service Appliance Category </td>
    </tr>
        <tr>
        <td>shared</td><td>Set the accessibility of the nsappliance category for other tenants</td>
    </tr>
</table>







#####1.5  Delete a Network Service Appliance Category

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>DELETE </td><td>/nsappliances/category/id </td><td> Delete a specified Network Service Appliance Category </td>
    </tr>
</table>

Normal Response Code(s): 204

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404), itemInUse (409)

This operation deletes a specified Network Service instance from the system.

Specify the ID for the Network Service Appliance Category as id in the URI.

This operation does not require a request body or return a response body.

#####1.6  List Network Functions


<table cellspacing = 30  >
    <tr>
    <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>GET </td><td> /nsappliances/networkfunction </td><td> List all network Functions</td>
    </tr>
</table>

Normal Response Code(s): 200, 203

Error Response Codes(s): computeFault (400, 500), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413)

Example JSON response

    {
        "networkfunctions": 
        [
            {
                "id": "52415800-8b69-11e0-9b19-734f6af67565",
                "name":"UTM-service"
               
            },
            {
                "id": "493454534-8b69-11e0-9b19-74f6af672345",
                "name":"Firewall-Service"
            }
        ]
    }




#####1.7  create a Network Function



<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>POST </td><td>/nsappliances/networkfunctions </td><td> Create a network Function</td>
    </tr> 
</table>

Normal Response Code(s): 202

Error Response Code(s): computeFault (400, 500), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404), badMediaType (415), serverCapacityUnavailable (503)

This operation creates a network Function Catalogue. Each Network function is identified by UUID.

The following table describes the required and optional attributes that you can specify in the request body.

<table cellspacing = 30  >
    <tr>
        <th>Name</th><th>Description</th><th>Required</th>
    </tr>
    <tr>
        <td>name</td><td>The name of network function </td><td>Yes</td>
    </tr>
</table>

*Network Function create JSON request*


    {
        "name": "firewall"
    }


*Network Function create JSON response*


    {
        "id": "52415800-8b69-11e0-9b19-734f565bc83b",
        "category": "firewall"
 
    }





#####1.8  Get Network Functions Catalog Details


<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>GET </td><td>/nsappliances/networkfunctions/{function_id} </td><td> List details of a specified network Function </td>
    </tr>
</table>

Normal Response Code(s): 200, 203

Error Response Code(s): computeFault (400, 500), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404)

Specify the Network Function ID as id in the URI.

This operation does not require a request body.

This operation returns the details of a specific Network Service Appliance Category by its ID.

*Example JSON response*


    {
        "id": "52415800-8b69-11e0-9b19-734f565bc83b",
        "name": "firewall"
    }






#####1.9  Update a Network Function Name


<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>PUT </td><td>/nsappliances/networkfunctions/{function_id} </td><td> Update a specified Network Function name</td>
    </tr>
</table>

Normal Response Code(s): 200

Error Response Code(s): computeFault (400, 500), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404)

This operation enables you to update the editable attributes of a specified Network Function.

Specify the Network Function ID as id in the URI.

The following table describes the attributes that you can specify in the request body:

<table cellspacing = 30  >
    <tr>
        <th>Name</th><th>Description</th>
    </tr>
    <tr>
        <td>name</td><td>You can edit the description of this Network Function name </td>
    </tr>
</table>







#####1.10  Delete a Network Function

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>DELETE </td><td>/nsappliances/category/id </td><td> Delete a specified Network Function </td>
    </tr>
</table>

Normal Response Code(s): 204

Error Response Code(s): computeFault (400, 500,), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404), itemInUse (409)

This operation deletes a specified Network Function from the system.

Specify the ID for the Network function id in the URI.

This operation does not require a request body or return a response body.





##2.0  Network Service Appliance Image Management

The following set of APIs are to manage Images for the configured Network Service Appliances.

#####2.1  List Image mappings for a Network Service Appliance

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>GET </td><td>/nsappliances/category/{category_id}/imagemap</td><td>List all Network Service Appliance images for a specified Category</td>
    </tr>
</table>

Normal Response Code(s): 200, 203
Error Response Codes(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413)

Example JSON response


    {
    "imagemap": [
        {
            "id": "52415800-8b69-11e0-9b19-734f6af67565",
            "tenant-id": "11415800-8b69-11e0-9b19-734f6af67522",
            "name": "iptables-appliance",
            "imageRef": "http://servers.api.openstack.org/1234/images/52415800-8b69-11e0-9b19-734f6f006e54",
            "flavorRef": "52415800-8b69-11e0-9b19-734f1195ff37",
            "metadata": {
                "My Server Name": "iptables-perimeter-firewall"
            },
            "personality": [
                {
                    "path": "/etc/banner.txt",
                    "contents": "ICAgICAgDQoiQSBjbG91ZCBkb2VzIG5vdCBrbm93IHdoeSBp dCBtb3ZlcyBpbiBqdXN0IHN1Y2ggYSBkaXJlY3Rpb24gYW5k IGF0IHN1Y2ggYSBzcGVlZC4uLkl0IGZlZWxzIGFuIGltcHVs c2lvbi4uLnRoaXMgaXMgdGhlIHBsYWNlIHRvIGdvIG5vdy4g QnV0IHRoZSBza3kga25vd3MgdGhlIHJlYXNvbnMgYW5kIHRo ZSBwYXR0ZXJucyBiZWhpbmQgYWxsIGNsb3VkcywgYW5kIHlv dSB3aWxsIGtub3csIHRvbywgd2hlbiB5b3UgbGlmdCB5b3Vy c2VsZiBoaWdoIGVub3VnaCB0byBzZWUgYmV5b25kIGhvcml6 b25zLiINCg0KLVJpY2hhcmQgQmFjaA=="
                }
            ]
        },
        {
            "id": "12415800-8b69-11e0-9b19-734f6af67565",
            "tenant-id": "11415800-8b69-11e0-9b19-734f6af67522",
            "name": "waf-appliance",
            "imageRef": "http://servers.api.openstack.org/1234/images/12415800-8b69-11e0-9b19-734f6f006e54",
            "flavorRef": "12415800-8b69-11e0-9b19-734f1195ff37",
            "metadata": {
                "My Server Name": "web-application-firewall"
            },
            "personality": [
                {
                    "path": "/etc/banner.txt",
                    "contents": "ICAgICAgDQoiQSBjbG91ZCBkb2VzIG5vdCBrbm93IHdoeSBp dCBtb3ZlcyBpbiBqdXN0IHN1Y2ggYSBkaXJlY3Rpb24gYW5k IGF0IHN1Y2ggYSBzcGVlZC4uLkl0IGZlZWxzIGFuIGltcHVs c2lvbi4uLnRoaXMgaXMgdGhlIHBsYWNlIHRvIGdvIG5vdy4g QnV0IHRoZSBza3kga25vd3MgdGhlIHJlYXNvbnMgYW5kIHRo ZSBwYXR0ZXJucyBiZWhpbmQgYWxsIGNsb3VkcywgYW5kIHlv dSB3aWxsIGtub3csIHRvbywgd2hlbiB5b3UgbGlmdCB5b3Vy c2VsZiBoaWdoIGVub3VnaCB0byBzZWUgYmV5b25kIGhvcml6 b25zLiINCg0KLVJpY2hhcmQgQmFjaA=="
                }
            ]
        }
    ]
    }
    




#####2.2  Create Image map for a given Network Service Appliance Cateogry


<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>POST </td><td>/nsappliances/category/{category_id}/imagemap </td><td>Create a Image map of a specified Network Service Appliance Category </td>
    </tr>
</table>

Normal Response Code(s): 202

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404), badMediaType (415), serverCapacityUnavailable (503)

This operation creates a Image mapping for a Network Service Appliance Category. 

This API does not upload any new images but refers to existing Image in Glance. It creates a mapping with existing Image with NS Appliance Category.

The following table describes the required and optional attributes that you can specify in the request body.

<table cellspacing = 30  >
    <tr>
        <th>Name</th><th>Description</th><th>Required</th>
    </tr>
    <tr>
        <td>name</td><td>Name of the Image map</td><td>True</td>
    </tr>
    <tr>
        <td>imageRef</td><td>The image reference for the desired image for your NS Appliance.Specify as an ID or full URL.</td><td>True</td>
    </tr>
    <tr>
        <td>flavorRef</td><td>The flavor reference for the desired flavor for your NS Appliance.Specify as an ID or full URL. </td><td>True</td>
        
    </tr>
        <td>metadata</td><td>Metadata key and value pairs. For information, see openstack docsÃ¢â‚¬Â.</td><td>False</td>
    </tr>
    <tr>
        <td>personality</td><td>File path and contents. For information, see openstack docs</td><td>False</td>
    </tr>
</table>



*NS Appliance Image map create JSON request*


    {
        "name": "waf-appliance",
        "imageRef" :"http://servers.api.openstack.org/1234/images/52415800-8b69-11e0-9b19-734f6f006e54",
        "flavorRef" : "52415800-8b69-11e0-9b19-734f1195ff37",
        "metadata" : {
           "My Server Name" : "web-application-firewall"
        },
        "personality" : [
            {          
                "path" : "/etc/banner.txt",
                "contents" : "ICAgICAgDQoiQSBjbG91ZCBkb2VzIG5vdCBrbm93IHdoeSBp dCBtb3ZlcyBpbiBqdXN0IHN1Y2ggYSBkaXJlY3Rpb24gYW5k IGF0IHN1Y2ggYSBzcGVlZC4uLkl0IGZlZWxzIGFuIGltcHVs c2lvbi4uLnRoaXMgaXMgdGhlIHBsYWNlIHRvIGdvIG5vdy4g QnV0IHRoZSBza3kga25vd3MgdGhlIHJlYXNvbnMgYW5kIHRo ZSBwYXR0ZXJucyBiZWhpbmQgYWxsIGNsb3VkcywgYW5kIHlv dSB3aWxsIGtub3csIHRvbywgd2hlbiB5b3UgbGlmdCB5b3Vy c2VsZiBoaWdoIGVub3VnaCB0byBzZWUgYmV5b25kIGhvcml6 b25zLiINCg0KLVJpY2hhcmQgQmFjaA=="
            } 
        ]
    }
                   


*NS Appliance create image map JSON response*



    {
        "imagemap": {
            "id": "52415800-8b69-11e0-9b19-734f565bc83b",
            "tenant_id": "1234",
            "name": "waf-appliance",
            "image": {
                "id": "52415800-8b69-11e0-9b19-734f6f006e54",
                "name": "WAF 1.2",
                "links": [
                    {
                        "rel": "self",
                        "href": "http://servers.api.openstack.org/v2/1234/images/52415800-8b69-11e0-9b19-734f6f006e54"
                    },
                    {
                        "rel": "bookmark",
                        "href": "http://servers.api.openstack.org/1234/images/52415800-8b69-11e0-9b19-734f6f006e54"
                    }
                ]
            },
            "flavor": {
                "id": "52415800-8b69-11e0-9b19-734f1195ff37",
                "name": "256 MB Server",
                "links": [
                    {
                        "rel": "self",
                        "href": "http://servers.api.openstack.org/v2/1234/flavors/52415800-8b69-11e0-9b19-734f1195ff37"
                    },
                    {
                        "rel": "bookmark",
                        "href": "http://servers.api.openstack.org/1234/flavors/52415800-8b69-11e0-9b19-734f1195ff37"
                    }
                ]
            },
            "metadata": {
                "My Server Name": "web-application-firewall"
            }
        }
    }






#####2.3  Get image map for NS Appliance Details


<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>GET </td><td>/nsappliances/category/{category_id}/imagemap/{imagemap_id} </td><td> List details of a specified image of a specified NS Appliance category</td>
    </tr>
</table>

Normal Response Code(s): 200, 203

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404)

Specify the imagemap ID as {imagemap_id} and NS Appliance Category ID as cateogry_id in the URI.

This operation does not require a request body.

This operation returns the details of a specific NS Appliance Image map by its ID.

*Example JSON response*


    {
        "imagemap": {
            "id": "52415800-8b69-11e0-9b19-734f565bc83b",
            "tenant_id": "1234",
            "name": "waf-appliance",
            "image": {
                "id": "52415800-8b69-11e0-9b19-734f6f006e54",
                "name": "WAF 1.2",
                "links": [
                    {
                        "rel": "self",
                        "href": "http://servers.api.openstack.org/v2/1234/images/52415800-8b69-11e0-9b19-734f6f006e54"
                    },
                    {
                        "rel": "bookmark",
                        "href": "http://servers.api.openstack.org/1234/images/52415800-8b69-11e0-9b19-734f6f006e54"
                    }
                ]
            },
            "flavor": {
                "id": "52415800-8b69-11e0-9b19-734f1195ff37",
                "name": "256 MB Server",
                "links": [
                    {
                        "rel": "self",
                        "href": "http://servers.api.openstack.org/v2/1234/flavors/52415800-8b69-11e0-9b19-734f1195ff37"
                    },
                    {
                        "rel": "bookmark",
                        "href": "http://servers.api.openstack.org/1234/flavors/52415800-8b69-11e0-9b19-734f1195ff37"
                    }
                ]
            },
            "metadata": {
                "My Server Name": "web-application-firewall"
            }
        }
    }





#####2.4  Update Image map for a given NS Appliance Category

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>PUT </td><td> /nsappliances/category/{category_id}/imagemap/{imagemap_id}</td><td> Update a specified Image map of a specified NS Appliance Category</td>
    </tr>
</table>

Normal Response Code(s): 200

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404)

This operation enables you to update the editable attributes of a specified NS Appliance Category Image mapping.

Specify the NS Appliance Category ID as category_id and imagemap ID as imagemap_id in the URI.

This request requires a body. Chaning parameters other than the specified attributes will result in 400 Bad request error.

The following table describes the attributes that you can specify in the request body:

<table cellspacing = 30  >
    <tr>
        <th>Name</th><th>Description</th>
    </tr>
    <tr>
        <td>name</td><td>Change the Image mapping name</td>
    </tr>
</table>






#####2.5  Delete a image map in NS Appliance Category

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>DELETE </td><td>/nsappliances/category/{category_id}/imagemap/{imagemap_id}</td><td>Delete a specified image map of a NS Appliance Category </td>
    </tr>
</table>

Normal Response Code(s): 204

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404), itemInUse (409)

This operation deletes a specified Network Service Appliance Category imagemap from the system.

Specify the ID for the NS Appliance Category as category id and Image Mapping ID in imagemap id

This operation does not require a request body or return a response body.





##3.0  NS Appliance Chain Management

#####3.1  List all NS Appliance chains


<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>GET </td><td> /nsapplainces/chain </td><td>List all NS Appliance Chains</td>
    </tr>
</table>
Normal Response Code(s): 200, 203

Error Response Codes(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413)

Example JSON response


    {
        "chain": [
            {
                "id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                "tenant-id": "4b38f464-5890-4bed-8c75-24e88e366d4c",
                "name": "security services chain",
                "nsappliances-imagemaps": [
                    "edb70004-5499-4a78-a8cd-a708ff44e087",
                    "3fa754ad-07cd-45e6-8ff2-e353a8d5051e",
                    "daa512af-eb6a-4e72-8db6-451978188d33"
                ]
            },
            {
                "id": "11b63baa-8010-4873-b040-1d886e39fd8b",
                "tenant-id": "4b38f464-5890-4bed-8c75-24e88e366d4c",
                "name": "value added network servers chain",
                "nsappliances-imagemaps": [
                    "aab70004-5499-4a78-a8cd-a708ff44e087",
                    "bb754ad-07cd-45e6-8ff2-e353a8d5051e"
                ]
            }
        ]
    }







#####3.2  Create a NS Appliance Chain


<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>POST </td><td> /nsappliances/chain </td><td> Create a NS Appliances Chain</td>
    </tr>
</table>

Normal Response Code(s): 202

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404), badMediaType (415), serverCapacityUnavailable (503)

This operation creates a NS Appliance Image map chain. Each Chain is identified by UUID.

Further information to fulfil the NS Appliance Chain is provided in other APIs.

The chain will be created with the list of NS Appliances provided in the same order given. For example, if user wants NS applainces in the order of firewall, VPN, firewall, IPS. Then user to have send Image maps of those Network Serivce Appliances in the same order in this Request. 

The following table describes the required and optional attributes that you can specify in the request body.

<table cellspacing = 30  >
    <tr>
        <th>Name</th><th>Description</th><th>Required</th>
    </tr>
    <tr>
        <td>name</td><td>Name of the NS Appliance Chain </td><td>False</td>
    </tr>
    <tr>
        <td>id</td><td>List of NS Appliance Image maps. The order is important </td><td>Yes</td>
    </tr>
</table>

*NS Appliance chain create JSON request*


    {
         "name": "security services chain"
         "nsappliances-imagemaps": [
            "edb70004-5499-4a78-a8cd-a708ff44e087",
            "3fa754ad-07cd-45e6-8ff2-e353a8d5051e",
            "daa512af-eb6a-4e72-8db6-451978188d33"
          ]
   
    }          


*NS Appliance Chain create JSON response*

    {
        "id": "36b63baa-8010-4873-b040-1d886e39fd8b",
         "tenant-id":"4b38f464-5890-4bed-8c75-24e88e366d4c",
         "name": "security services chain"
         "nsappliances-imagemaps": [
            "edb70004-5499-4a78-a8cd-a708ff44e087",
            "3fa754ad-07cd-45e6-8ff2-e353a8d5051e",
            "daa512af-eb6a-4e72-8db6-451978188d33"
          ]
    }






#####3.3  Get details of a NS Appliance Chain

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>GET </td><td>/nsappliances/chain/{chain_id} </td><td> List details of a specified NS Appliance Chain</td>
    </tr>
</table>

Normal Response Code(s): 200, 203

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404)

Specify the Network Service Appliance Chain ID as id in the URI.

This operation does not require a request body.

This operation returns the details of a specific Network Service Appliance Chain by its ID.

*Example JSON response*


    {
        "id": "36b63baa-8010-4873-b040-1d886e39fd8b",
         "tenant-id":"4b38f464-5890-4bed-8c75-24e88e366d4c",
         "name": "security services chain"
         "nsappliances-imagemaps": [
            "edb70004-5499-4a78-a8cd-a708ff44e087",
            "3fa754ad-07cd-45e6-8ff2-e353a8d5051e",
            "daa512af-eb6a-4e72-8db6-451978188d33"
          ]
    }






#####3.4  update a NS Appliance Chain

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>PUT </td><td> /nsappliances/chain/{chain_id}</td><td> Update a specified NS Appliance Chain/td>
    </tr>
</table>

Normal Response Code(s): 200

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404)

This operation updates the attributes of NS Appliance Chain of a specified chain_id.

The following table describes the attributes that you can specify in the request body:

<table cellspacing = 30  >
    <tr>
        <th>Name</th><th>Description</th>
    </tr>
    <tr>
        <td>name</td><td>Change the Chain name</td>
    </tr>
        <tr>
        <td>nsappliances-imagemap-ids</td><td>Change the image maps for the chain</td>
    </tr>
</table>








#####3.5  Delete a NS Appliance Chain

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>DELETE </td><td>/nsappliances/chain/{chain_id}</td><td>Delete a specified Chain of NS Appliances </td>
    </tr>
</table>

Normal Response Code(s): 204

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404), itemInUse (409)

This operation deletes a specified Network Service Appliances Chain from the system.

Specify the ID for the NS Appliances Chain as the chain_id

This operation does not require a request body or return a response body.






##4.0  NS Rule List Management


#####4.1 List Network Rules


<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>GET </td><td>/nsappliances/rules</td><td>List all network rules </td>
    </tr>
</table>


Normal Response Code(s): 200, 203

Error Response Codes(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413)

*Example JSON response*

    {
        "rules": [
            {
                "id": "5241c37f-25b5-4d92-bb3c-a66b2c112789",
                "name": "my custom rule1",
                "prev": "None",
                "next": "8be232a2-e63f-4638-ba83-fb8f129d8d9f",
                "l2": {
                    "src-mac": [
                        "9d:72:38:b4:0b:11",
                        "2c:41:38:b4:0b:58"
                    ],
                    "dst-mac": [
                        "any"
                    ],
                    "vlan": {
                        "range": {
                            "start": 100,
                            "end": 200
                        },
                        "list": [
                            500,
                            560
                        ]
                    }
                },
                "l3": {
                    "version": 4,
                    "src-addr": {
                        "range": {
                            "start": "192.168.0.6",
                            "end": "192.168.0.0.110"
                        },
                        "list": [
                            "192.168.0.200",
                            "192.168.0.205"
                        ],
                        "net-info": {
                            "network": "10.1.10.0",
                            "netmask": "255.255.255.0"
                        }
                    },
                    "dst-addr": {
                        "range": {
                            "start": "192.168.1.6",
                            "end": "192.168.0.1.110"
                        },
                        "list": [
                            "192.168.1.200",
                            "192.168.1.205"
                        ],
                        "net-info": {
                            "network": "10.2.10.0",
                            "netmask": "255.255.255.0"
                        }
                    },
                    "protocol": [
                        "tcp",
                        "udp"
                    ]
                },
                "l4": {
                    "src-port": {
                        "range": {
                            "start": 2048,
                            "end": 3048
                        },
                        "list": [
                            6000,
                            6600
                        ]
                    },
                    "dst-port": {
                        "range": {
                            "start": 15,
                            "end": 2048
                        },
                        "list": [
                            8080,
                            5000
                        ]
                    }
                },
                "action": {
                    "bypass": {
                        "imagemap-ids": [
                            "283f1ddb-5262-4ec5-9fb7-cbf4d0eed79f",
                            "899aedc8-2ce8-436d-977c-94a7268fb0b0"
                        ]
                    }
                }
            },
            {
                "id": "77b4b4b2-5d80-41d6-a10f-fa5e0fa75a2d",
                "name": "my custom rule2",
                "prev": "5241c37f-25b5-4d92-bb3c-a66b2c112789",
                "next":"None",
                "l2": {
                    "src-mac": [
                        "any"
                    ],
                    "dst-mac": [
                        "any"
                    ],
                    "vlan": {
                        "list": [
                            "any"
                        ]
                    }
                },
                "l3": {
                    "version": 4,
                    "src-addr": {
                        "range": {
                            "start": "192.168.0.6",
                            "end": "192.168.0.0.110"
                        },
                        "list": [
                            "192.168.0.200",
                            "192.168.0.205"
                        ],
                        "net-info": {
                            "network": "10.1.10.0",
                            "netmask": "255.255.255.0"
                        }
                    },
                    "dst-addr": {
                        "list": [
                            "any"
                        ]
                    },
                    "protocol": [
                        "any"
                    ]
                },
                "l4": {
                    "src-port": {
                        "list": [
                            "any"
                        ]
                    },
                    "dst-port": {
                        "range": {
                            "start": 15,
                            "end": 2048
                        },
                        "list": [
                            8080,
                            5000
                        ]
                    }
                },
                "action": {
                    "bypass": {
                        "imagemap-ids": [
                            "74c0be55-80eb-4fe6-835e-62b710982381"
                        ]
                    }
                }
            }
        ]
    }







#####4.2 Create a Network rule

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>POST </td><td>/nsappliances/rules </td><td>Create a network rule</td>
    </tr>
</table>

Normal Response Code(s): 202

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404), badMediaType (415), serverCapacityUnavailable (503)

This operation creates a network rule. Each rule is identified by UUID.

Following table lists the description of the fields used in the JSON Request.
Note that rules are prioritized as per the order in the JSON request.


<table cellspacing = 30  >
    <tr>
        <th>Name</th><th>Description</th><th>Required</th>
    </tr>
    <tr>
        <td>name</td><td>Name of the Network rule list </td><td>False</td>
    </tr>
    <tr>
        <td>prev</td><td>UUID of previous rule. This along with next field helps to insert a rule between those rules. If prev is None then this is the first rule</td><td>False</td>
    </tr>
    <tr>
        <td>next</td><td>UUID of the next rule. Next will be None for the last rule</td><td>False</td>
    </tr>
    <tr>
        <td>name</td><td>Name of the Network rule list </td><td>False</td>
    </tr>
    <tr>
        <td>src-mac</td><td>Source MAC address. Specify a list of MACs </td><td>False</td>
    </tr>
    <tr>
        <td>dst-mac</td><td>Destination MAC address. Specify List of MACs</td><td>False</td>
    </tr>
    <tr>
        <td>vlan</td><td>VLAN of the packet. Specify a custom range and/or list of VLANs </td><td>False</td>
    </tr>
    <tr>
        <td>version</td><td>IP version. Can set to to 4 for IPv4 and 6 for IPv6 </td><td>False</td>
    </tr>
    <tr>
        <td>src-addr</td><td>Source IP Address. Can be range with start and end specified or list of IP addresses or a subnet with mask or combination of them </td><td>False</td>
    </tr>
    <tr>
        <td>dst-addr</td><td>Destination IP Address. Can be range with start and end specified or list of IP addresses or a subnet with mask or combination of them </td><td>False</td>
    </tr>
    <tr>
        <td>protocol</td><td>IP Protocol. </td><td>False</td>
    </tr>
    <tr>
        <td>src-port</td><td>TCP or UDP port. It can be range or list of ports</td><td>False</td>
    </tr>
    <tr>
        <td>dst-port</td><td>TCP or UDP port. It can be range or list of ports</td><td>False</td>
    </tr>
    <tr>
        <td>bypass</td><td>Action Bypass for the specified NS Appliance imagemap IDs</td><td>Yes</td>
    </tr>
    <tr>
        <td>imagemap-ids</td><td>List of NS Appliance Imagemap IDs</td><td>Yes</td>
    </tr>

</table>

*Example JSON Request*

    {
        "name": "my custom rule1",
        "prev":"de598b3a-aeef-4fe1-ba32-479be8372a71",
        "next":"759e5dcf-5a8a-4b0a-b25f-373437770065",
        "l2": {
            "src-mac": [
                "9d:72:38:b4:0b:11",
                "2c:41:38:b4:0b:58"
            ],
            "dst-mac": [
                "any"
            ],
            "vlan": {
                "range": {
                    "start": 100,
                    "end": 200
                },
                "list": [
                    500,
                    560
                ]
            }
        },
        "l3": {
            "version": 4,
            "src-addr": {
                "range": {
                    "start": "192.168.0.6",
                    "end": "192.168.0.0.110"
                },
                "list": [
                    "192.168.0.200",
                    "192.168.0.205"
                ],
                "net-info": {
                    "network": "10.1.10.0",
                    "netmask": "255.255.255.0"
                }
            },
            "dst-addr": {
                "range": {
                    "start": "192.168.1.6",
                    "end": "192.168.0.1.110"
                },
                "list": [
                    "192.168.1.200",
                    "192.168.1.205"
                ],
                "net-info": {
                    "network": "10.2.10.0",
                    "netmask": "255.255.255.0"
                }
            },
            "protocol": [
                "tcp",
                "udp"
            ]
        },
        "l4": {
            "src-port": {
                "range": {
                    "start": 2048,
                    "end": 3048
                },
                "list": [
                    6000,
                    6600
                ]
            },
            "dst-port": {
                "range": {
                    "start": 15,
                    "end": 2048
                },
                "list": [
                    8080,
                    5000
                ]
            }
        },
        "action": {
            "bypass": {
                "imagemap-ids": [
                    "283f1ddb-5262-4ec5-9fb7-cbf4d0eed79f",
                    "899aedc8-2ce8-436d-977c-94a7268fb0b0"
                ]
            }
        }
    }



*Example JSON Response*

    {
        "id": "5241c37f-25b5-4d92-bb3c-a66b2c112789",
        "name": "my custom rule1",
        "prev":"de598b3a-aeef-4fe1-ba32-479be8372a71",
        "next":"759e5dcf-5a8a-4b0a-b25f-373437770065",
        "l2": {
            "src-mac": [
                "9d:72:38:b4:0b:11",
                "2c:41:38:b4:0b:58"
            ],
            "dst-mac": [
                "any"
            ],
            "vlan": {
                "range": {
                    "start": 100,
                    "end": 200
                },
                "list": [
                    500,
                    560
                ]
            }
        },
        "l3": {
            "version": 4,
            "src-addr": {
                "range": {
                    "start": "192.168.0.6",
                    "end": "192.168.0.0.110"
                },
                "list": [
                    "192.168.0.200",
                    "192.168.0.205"
                ],
                "net-info": {
                    "network": "10.1.10.0",
                    "netmask": "255.255.255.0"
                }
            },
            "dst-addr": {
                "range": {
                    "start": "192.168.1.6",
                    "end": "192.168.0.1.110"
                },
                "list": [
                    "192.168.1.200",
                    "192.168.1.205"
                ],
                "net-info": {
                    "network": "10.2.10.0",
                    "netmask": "255.255.255.0"
                }
            },
            "protocol": [
                "tcp",
                "udp"
            ]
        },
        "l4": {
            "src-port": {
                "range": {
                    "start": 2048,
                    "end": 3048
                },
                "list": [
                    6000,
                    6600
                ]
            },
            "dst-port": {
                "range": {
                    "start": 15,
                    "end": 2048
                },
                "list": [
                    8080,
                    5000
                ]
            }
        },
        "action": {
            "bypass": {
                "imagemap-ids": [
                    "283f1ddb-5262-4ec5-9fb7-cbf4d0eed79f",
                    "899aedc8-2ce8-436d-977c-94a7268fb0b0"
                ]
            }
        }
    }

#####4.3  Get details of a Network Rule

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>GET </td><td>/nsappliances/rules/{rule_id} </td><td> List details of a specified Network rule</td>
    </tr>
</table>

Normal Response Code(s): 200, 203

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404)

Specify the Network Rule ID as id in the URI.

This operation does not require a request body.

This operation returns the details of a specific Network Rule by its ID

*Example JSON response*




    {
        "id": "5241c37f-25b5-4d92-bb3c-a66b2c112789",
        "name": "my custom rule1",
        "prev":"de598b3a-aeef-4fe1-ba32-479be8372a71",
        "next":"759e5dcf-5a8a-4b0a-b25f-373437770065",
        "l2": {
            "src-mac": [
                "9d:72:38:b4:0b:11",
                "2c:41:38:b4:0b:58"
            ],
            "dst-mac": [
                "any"
            ],
            "vlan": {
                "range": {
                    "start": 100,
                    "end": 200
                },
                "list": [
                    500,
                    560
                ]
            }
        },
        "l3": {
            "version": 4,
            "src-addr": {
                "range": {
                    "start": "192.168.0.6",
                    "end": "192.168.0.0.110"
                },
                "list": [
                    "192.168.0.200",
                    "192.168.0.205"
                ],
                "net-info": {
                    "network": "10.1.10.0",
                    "netmask": "255.255.255.0"
                }
            },
            "dst-addr": {
                "range": {
                    "start": "192.168.1.6",
                    "end": "192.168.0.1.110"
                },
                "list": [
                    "192.168.1.200",
                    "192.168.1.205"
                ],
                "net-info": {
                    "network": "10.2.10.0",
                    "netmask": "255.255.255.0"
                }
            },
            "protocol": [
                "tcp",
                "udp"
            ]
        },
        "l4": {
            "src-port": {
                "range": {
                    "start": 2048,
                    "end": 3048
                },
                "list": [
                    6000,
                    6600
                ]
            },
            "dst-port": {
                "range": {
                    "start": 15,
                    "end": 2048
                },
                "list": [
                    8080,
                    5000
                ]
            }
        },
        "action": {
            "bypass": {
                "imagemap-ids": [
                    "283f1ddb-5262-4ec5-9fb7-cbf4d0eed79f",
                    "899aedc8-2ce8-436d-977c-94a7268fb0b0"
                ]
            }
        }
    }


#####4.4 Update a network rule

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>PUT </td><td> /nsapplainces/rules/{rule_id} </td><td>Update a specified Network rule</td>
    </tr>
</table>


Normal Response Code(s): 200

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404)

This operation updates the attributes of NS Appliance Rule of a specified rule_id

The following table describes the attributes that you can specify in the request body:



<table cellspacing = 30  >
    <tr>
        <th>Name</th><th>Description</th><th>Required</th>
    </tr>
    <tr>
        <td>name</td><td>Name of the Network rule list </td><td>False</td>
    </tr>
    <tr>
        <td>prev</td><td>UUID of previous rule. This along with next field helps to insert a rule between those rules. If prev is None then this is the first rule</td><td>False</td>
    </tr>
    <tr>
        <td>next</td><td>UUID of the next rule. Next will be None for the last rule</td><td>False</td>
    </tr>
    <tr>
        <td>src-mac</td><td>Source MAC address. Specify a list of MACs </td><td>False</td>
    </tr>
    <tr>
        <td>dst-mac</td><td>Destination MAC address. Specify List of MACs</td><td>False</td>
    </tr>
    <tr>
        <td>vlan</td><td>VLAN of the packet. Specify a custom range and/or list of VLANs </td><td>False</td>
    </tr>
    <tr>
        <td>version</td><td>IP version. Can set to to 4 for IPv4 and 6 for IPv6. Default must be IPv4 </td><td>False</td>
    </tr>
    <tr>
        <td>src-addr</td><td>Source IP Address. Can be range with start and end specified or list of IP addresses or a subnet with mask or combination of them </td><td>False</td>
    </tr>
    <tr>
        <td>dst-addr</td><td>Destination IP Address. Can be range with start and end specified or list of IP addresses or a subnet with mask or combination of them </td><td>False</td>
    </tr>
    <tr>
        <td>protocol</td><td>IP Protocol. </td><td>False</td>
    </tr>
    <tr>
        <td>src-port</td><td>TCP or UDP port. It can be range or list of ports</td><td>False</td>
    </tr>
    <tr>
        <td>dst-port</td><td>TCP or UDP port. It can be range or list of ports</td><td>False</td>
    </tr>
    <tr>
        <td>bypass</td><td>Action Bypass for the specified NS Appliance imagemap IDs</td><td>Yes</td>
    </tr>
    <tr>
        <td>imagemap-ids</td><td>List of NS Appliance Imagemap IDs</td><td>Yes</td>
    </tr>

</table>

*Example JSON Request*




    {
        "id": "5241c37f-25b5-4d92-bb3c-a66b2c112789",
        "name": "my custom rule1",
        "prev":"None",
        "next":"759e5dcf-5a8a-4b0a-b25f-373437770065",
    }


*Example JSON Response*



    {
        "id": "5241c37f-25b5-4d92-bb3c-a66b2c112789",
        "name": "my custom rule1",
        "prev":"None",
        "next":"759e5dcf-5a8a-4b0a-b25f-373437770065",
        "l2": {
            "src-mac": [
                "9d:72:38:b4:0b:11",
                "2c:41:38:b4:0b:58"
            ],
            "dst-mac": [
                "any"
            ],
            "vlan": {
                "range": {
                    "start": 100,
                    "end": 200
                },
                "list": [
                    500,
                    560
                ]
            }
        },
        "l3": {
            "version": 4,
            "src-addr": {
                "range": {
                    "start": "192.168.0.6",
                    "end": "192.168.0.0.110"
                },
                "list": [
                    "192.168.0.200",
                    "192.168.0.205"
                ],
                "net-info": {
                    "network": "10.1.10.0",
                    "netmask": "255.255.255.0"
                }
            },
            "dst-addr": {
                "range": {
                    "start": "192.168.1.6",
                    "end": "192.168.0.1.110"
                },
                "list": [
                    "192.168.1.200",
                    "192.168.1.205"
                ],
                "net-info": {
                    "network": "10.2.10.0",
                    "netmask": "255.255.255.0"
                }
            },
            "protocol": [
                "tcp",
                "udp"
            ]
        },
        "l4": {
            "src-port": {
                "range": {
                    "start": 2048,
                    "end": 3048
                },
                "list": [
                    6000,
                    6600
                ]
            },
            "dst-port": {
                "range": {
                    "start": 15,
                    "end": 2048
                },
                "list": [
                    8080,
                    5000
                ]
            }
        },
        "action": {
            "bypass": {
                "imagemap-ids": [
                    "283f1ddb-5262-4ec5-9fb7-cbf4d0eed79f",
                    "899aedc8-2ce8-436d-977c-94a7268fb0b0"
                ]
            }
        }
    }


#####4.5 Delete a Network Rule 

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>DELETE </td><td>/nsappliances/rules/{rule_id}</td><td>Delete a specified Rule</td>
    </tr>
</table>

Normal Response Code(s): 204

Error Response Code(s): computeFault (400, 500) serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404), itemInUse (409)

This operation deletes a specified Rule from the system.

Specify the ID for rule as rule_id

This operation does not require a request body or return a response body.





#####4.6 List network rule lists

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>GET </td><td>/nsappliances/rulelist </td><td>List all network rule lists </td>
    </tr>
</table>


Normal Response Code(s): 200, 203

Error Response Codes(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413)

*Example JSON response*

    {
        "rulelist": [
            {
                "id": "5241c37f-25b5-4d92-bb3c-a66b2c112789",
                "name": "my custom rule list",
                "rules": [
                    "fe33b4d6-e62a-47dd-a083-addf6f3708a3",
                    "3443c5bb-891c-4c10-a065-347f5a4b021c",
                    "9426cc53-88c9-49dd-a17f-95ed1272d0f0",
                    "f2f596ef-426b-4157-800c-062078ee24c8"
                ]
            },
            {
                "id": "ac8fd42a-a4d8-4f6a-96bd-eebeb8425a13",
                "name": "my simple rule list",
                "rules": [
                    "fe33b4d6-e62a-47dd-a083-addf6f3708a3",
                    "3443c5bb-891c-4c10-a065-347f5a4b021c"
                ]
            }
        ]
    }








#####4.7 Create a Network rule list

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>POST </td><td>/nsappliances/rulelist </td><td>Create a network rule lists </td>
    </tr>
</table>

Normal Response Code(s): 202

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404), badMediaType (415), serverCapacityUnavailable (503)

This operation creates a network rule list. Each rule list is identified by UUID.

Following table lists the description of the fields used in the JSON Request.
Note that rules are prioritized as per the order in the JSON request.


<table cellspacing = 30  >
    <tr>
        <th>Name</th><th>Description</th><th>Required</th>
    </tr>
    <tr>
        <td>name</td><td>Name of the Network rule list </td><td>No</td>
    </tr>
    <tr>
        <td>rules</td><td>List of network rules in the order of priority</td><td>Yes</td>
    </tr>

</table>

*Example JSON Request*

    {
        "name": "my custom rule list",
        "rules": [
            "fe33b4d6-e62a-47dd-a083-addf6f3708a3",
            "3443c5bb-891c-4c10-a065-347f5a4b021c",
            "9426cc53-88c9-49dd-a17f-95ed1272d0f0",
            "f2f596ef-426b-4157-800c-062078ee24c8"
        ]
    }

*Example JSON Response*

    {
        "id": "5241c37f-25b5-4d92-bb3c-a66b2c112789",
        "name": "my custom rule list",
        "rules": [
            "fe33b4d6-e62a-47dd-a083-addf6f3708a3",
            "3443c5bb-891c-4c10-a065-347f5a4b021c",
            "9426cc53-88c9-49dd-a17f-95ed1272d0f0",
            "f2f596ef-426b-4157-800c-062078ee24c8"
        ]
    }


#####4.8  Get details of a Network Rule list

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>GET </td><td>/nsappliances/rulelist/{rulelist_id} </td><td> List details of a specified Network rule list</td>
    </tr>
</table>

Normal Response Code(s): 200, 203

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404)

Specify the Network Rule list ID as id in the URI.

This operation does not require a request body.

This operation returns the details of a specific Network Rule list by its ID

*Example JSON response*

    {
        "id": "5241c37f-25b5-4d92-bb3c-a66b2c112789",
        "name": "my custom rule list",
        "rules": [
            "fe33b4d6-e62a-47dd-a083-addf6f3708a3",
            "3443c5bb-891c-4c10-a065-347f5a4b021c",
            "9426cc53-88c9-49dd-a17f-95ed1272d0f0",
            "f2f596ef-426b-4157-800c-062078ee24c8"
        ]
    }



#####4.9 Update a network rule list

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>PUT </td><td> /nsapplainces/rulelist/{rulelist_id} </td><td>Update a specified Network rule list</td>
    </tr>
</table>


Normal Response Code(s): 200

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404)

This operation updates the attributes of NS Appliance Rule list of a specified rulelist_id

The following table describes the attributes that you can specify in the request body:

An important use of PUT on this object is to change the rule priorities. User can shuffle the rules and update them as per the needs.

<table cellspacing = 30  >
    <tr>
        <th>Name</th><th>Description</th><th>Required</th>
    </tr>
    <tr>
        <td>name</td><td>Name of the Network rule list </td><td>False</td>
    </tr>
    <tr>
        <td>rules</td><td>List of network rules in the order of priority</td><td>Yes</td>
    </tr>

</table>

Example JSON Request

    {
        "name": "my modified custom rule list",
        "rules": [
            "3443c5bb-891c-4c10-a065-347f5a4b021c",
            "fe33b4d6-e62a-47dd-a083-addf6f3708a3",
            "f2f596ef-426b-4157-800c-062078ee24c8"
        ]
    }



*Example JSON Response*


    {
        "id": "5241c37f-25b5-4d92-bb3c-a66b2c112789",
        "name": "my modified custom rule list",
        "rules": [
            "3443c5bb-891c-4c10-a065-347f5a4b021c",
            "fe33b4d6-e62a-47dd-a083-addf6f3708a3",
            "f2f596ef-426b-4157-800c-062078ee24c8"
        ]
    }



#####4.10 Delete a Network Rule list 

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>DELETE </td><td>/nsappliances/rulelist/{rulelist_id}</td><td>Delete a specified Rule list </td>
    </tr>
</table>

Normal Response Code(s): 204

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404), itemInUse (409)

This operation deletes a specified Rule list ID from the system.

Specify the ID for rule list as rulelist_id

This operation does not require a request body or return a response body.



##5.0  NS Transparent Chain Management

#####5.1  List a transparent NS Appliance Chain

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>GET </td><td> /nsapplainces/transparentchains </td><td>List all NS Appliance Transparent Chains</td>
    </tr>
</table>
Normal Response Code(s): 200, 203

Error Response Codes(s): computeFault (400, 500), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413)

*Example JSON response*

        {
        "transparent-chains": [
            {
                "id": "ac9da911-6f83-4a14-afef-46a5ea308ab1",
                "name": "first transparent chain",
                "chain-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                "net-info": {
                    "networks": [
                        "3f8692d1-61aa-42ca-8967-fde1a5d0f084",
                        "cb302dcb-3375-410d-8ca2-8b7e07d2b6dd"
                    ]
                },
                "rulelist-id": "66f9746e-ad49-4a6f-a3fe-625b63e159f0",
                "nsappliances": [
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "7bc20e80-9af0-11e2-9e96-0800200c9a66",
                                "config-id": "9eba8119-2d0a-4210-bc26-9d3bad77e10f"
                            }
                        ]
                        
                    },
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "519a2b28-6a10-4833-abbe-51f0f149fb6f",
                                "config-id": "f62d5aed-7014-49d8-8fab-8a427c9592b5"
                            }
                        ]
                    },
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "3773d164-0b96-4c68-8c22-9642d55cc7b3",
                                "config-id": "7ef1fa64-9376-472b-99d9-31b2a4591acd"
                            }
                        ]
                        
                    }
                ]
            },
            {
                "id": "b85560ff-926a-425b-8a30-b617ec3eb1ee",
                "name": "a second transparent chain",
                "chain-id": "e84eb701-ccbf-42f3-82ff-80d83e38e1bb",
                "net-info": {
                    "networks": [
                        "f83eefb3-0c76-4083-978b-268db09f7a61",
                        "cb302dcb-3375-410d-8ca2-8b7e07d2b6dd"
                    ]
                },
                "rulelist-id": "c8037921-d421-4c55-944f-88181af1f50d",
                "nsappliances": [
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "c9431d2e-4032-44ca-9fe6-f293a0cd8813",
                                "config-id": "6b31bd8f-4f2d-46bf-8303-76f341ced23c"
                            }
                        ]
                        
                    }
                ]
            }
        ]
    }






#####5.2  Create a transparent NS Appliance Chain

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>POST </td><td>/nsappliances/transparentchains </td><td> Create a NS Appliance Transparent Chain</td>
    </tr> 
</table>

Normal Response Code(s): 202

Error Response Code(s): computeFault (400, 500), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404), badMediaType (415), serverCapacityUnavailable (503)

This operation creates a NS Appliance Transparent Chain. Each Transparent Chain is identified by UUID.

The following table describes the required and optional attributes that you can specify in the request body.

<table cellspacing = 30  >
    <tr>
        <th>Name</th><th>Description</th><th>Required</th>
    </tr>
    <tr>
        <td>name</td><td> Name of the transparent NS Appliance Chain </td><td>Yes</td>
    </tr>
    <tr>
        <td>chain-id</td><td>Create a NS Appliance Chain as specified by this chain model</td><td>Yes</td>
    </tr>
    <tr>
        <td>networks</td><td>Create a NS Appliance Chain between the networks specified. Must supply only two network-ids</td><td>Yes</td>
    </tr>
    <tr>
        <td>rulelist-id</td><td>A list of network rule list. Specify the rule list ID</td><td>Yes</td>
    </tr>
    <tr>
        <td>imagemap-id</td><td> NS Appliance image map id to use for the Appliance </td><td>Yes</td>
    </tr>
    <tr>
        <td>configs</td><td> NS Appliance Configuration list for each network function of the appliance </td><td>Yes</td>
    </tr>
    <tr>
        <td>max-instances</td><td> number of instances to run per appliance cluster. If not specified, default value is 1 </td><td>No</td>
    </tr>
    <tr>
        <td>flavorref</td><td> Flavor to use for the NS Appliance. If not specified the default values specified in image map are taken</td><td>No</td>
    </tr>
    <tr>
        <td>metadata </td><td> Metadata to supply to the NS Appliance instance. Default content overwritten if provided</td><td>No</td>
    </tr>
    <tr>
        <td>personality</td><td>Personality files to inject to NS Appliance instance. Default content overwritten if provided </td><td>No</td>
    </tr>

</table>


Transparent service chain should have two network entities.

*Create a Transparent NS Appliance Chain JSON Request*

            {
                "name": "first transparent chain",
                "chain-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                "net-info": {
                    "networks": [
                        "3f8692d1-61aa-42ca-8967-fde1a5d0f084",
                        "cb302dcb-3375-410d-8ca2-8b7e07d2b6dd"
                    ]
                },
                "rulelist-id": "66f9746e-ad49-4a6f-a3fe-625b63e159f0",
                "nsappliances": [
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "7bc20e80-9af0-11e2-9e96-0800200c9a66",
                                "config-id": "9eba8119-2d0a-4210-bc26-9d3bad77e10f"
                            }
                        ]
                        
                    },
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "519a2b28-6a10-4833-abbe-51f0f149fb6f",
                                "config-id": "f62d5aed-7014-49d8-8fab-8a427c9592b5"
                            }
                        ]
                    },
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "3773d164-0b96-4c68-8c22-9642d55cc7b3",
                                "config-id": "7ef1fa64-9376-472b-99d9-31b2a4591acd"
                            }
                        ]
                        
                    }
                ]
            }

*Create a Transparent NS Appliance Chain JSON Response*

            {
                "id": "ac9da911-6f83-4a14-afef-46a5ea308ab1",
                "name": "first transparent chain",
                "chain-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                "net-info": {
                    "networks": [
                        "3f8692d1-61aa-42ca-8967-fde1a5d0f084",
                        "cb302dcb-3375-410d-8ca2-8b7e07d2b6dd"
                    ]
                },
                "rulelist-id": "66f9746e-ad49-4a6f-a3fe-625b63e159f0",
                "nsappliances": [
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "7bc20e80-9af0-11e2-9e96-0800200c9a66",
                                "config-id": "9eba8119-2d0a-4210-bc26-9d3bad77e10f"
                            }
                        ]
                        
                    },
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "519a2b28-6a10-4833-abbe-51f0f149fb6f",
                                "config-id": "f62d5aed-7014-49d8-8fab-8a427c9592b5"
                            }
                        ]
                    },
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "3773d164-0b96-4c68-8c22-9642d55cc7b3",
                                "config-id": "7ef1fa64-9376-472b-99d9-31b2a4591acd"
                            }
                        ]
                        
                    }
                ]
            }





#####5.3  Get details of a transparent NS Appliance Chain

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>GET </td><td>/nsappliances/transparentchains/{chain_id} </td><td> List details of a specified Transparent NS Appliance Chain</td>
    </tr>
</table>

Normal Response Code(s): 200, 203

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404)

Specify the Network Service Appliance Transparent Chain ID as id in the URI.

This operation does not require a request body.

This operation returns the details of a specific Network Service Appliance Transparent Chain by its ID.

*Example JSON response*


            {
                "id": "ac9da911-6f83-4a14-afef-46a5ea308ab1",
                "name": "first transparent chain",
                "chain-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                "net-info": {
                    "networks": [
                        "3f8692d1-61aa-42ca-8967-fde1a5d0f084",
                        "cb302dcb-3375-410d-8ca2-8b7e07d2b6dd"
                    ]
                },
                "rulelist-id": "66f9746e-ad49-4a6f-a3fe-625b63e159f0",
                "nsappliances": [
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "7bc20e80-9af0-11e2-9e96-0800200c9a66",
                                "config-id": "9eba8119-2d0a-4210-bc26-9d3bad77e10f"
                            }
                        ]
                        
                    },
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "519a2b28-6a10-4833-abbe-51f0f149fb6f",
                                "config-id": "f62d5aed-7014-49d8-8fab-8a427c9592b5"
                            }
                        ]
                    },
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "3773d164-0b96-4c68-8c22-9642d55cc7b3",
                                "config-id": "7ef1fa64-9376-472b-99d9-31b2a4591acd"
                            }
                        ]
                        
                    }
                ]
            }
    





        
#####5.4  Update a transparent NS Appliance Chain

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>PUT </td><td>/nsappliances/transparentchains/{id} </td><td> Update a specified NS Appliance Transparent Chain</td>
    </tr>
</table>

Normal Response Code(s): 200

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404)

This operation enables you to update the editable attributes of a specified NS Appliance Transparent Chain

Specify the Network Service Appliance Transparent Chain ID as id in the URI.

The following table describes the attributes that you can specify in the request body:

<table cellspacing = 30  >
    <tr>
        <th>Name</th><th>Description</th>
    </tr>
    <tr>
        <td>name </td><td>You can change the NS Appliances Chain name </td><td>False</td>
    </tr>
    <tr>
        <td>networks</td><td>Change the network-ids that should have this chain</td><td>False</td>
    </tr>
    </tr>
    <tr>
        <td>rulelist-id</td><td>Change the Network rule list ID for this chain</td><td>False</td>
    </tr>
    <tr>
        <td>imagemap-id</td><td> NS Appliance image map id to use for the Appliance </td><td>False</td>
    </tr>
    <tr>
        <td>configs</td><td> NS Appliance Configuration list for each network function of the appliance </td><td>Yes</td>
    </tr>
    <tr>
        <td>max-instances</td><td> number of instances to run per appliance cluster. If not specified, default value is 1 </td><td>No</td>
    </tr>
    <tr>
        <td>flavorref</td> Flavor to use for the NS Appliance. If not specified the default values specified in image map are taken <td></td><td>No</td>
    </tr>
    <tr>
        <td>metadata </td><td> Metadata to supply to the NS Appliance instance. Default content overwritten if provided</td><td>No</td>
    </tr>
    <tr>
        <td>personality</td><td>Personality files to inject to NS Appliance instance. Default content overwritten if provided </td><td>No</td>
    </tr>
</table>

When network-ids gets changed, the implementation must terminate the NS Appliances for the old networks and create the NS Appliance chain between
the new networks.

If the nsappliances details gets changed, the instance has to terminated and re-created with the specified information.

*Update NS Transparent Chain JSON Request*

             {
 
                "name": "my first transparent chain",
                "chain-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                "net-info": {
                    "networks": [
                        "3f8692d1-61aa-42ca-8967-fde1a5d0f084",
                        "7241ea6d-1e35-4f21-83cc-e942a70e9dfd"
                    ]
                }
             }

    
*Update NS Transparent Chain JSON Response*

            {
                "id": "ac9da911-6f83-4a14-afef-46a5ea308ab1",
                "name": "first transparent chain",
                "chain-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                "net-info": {
                    "networks": [                        
                        "3f8692d1-61aa-42ca-8967-fde1a5d0f084",
                        "7241ea6d-1e35-4f21-83cc-e942a70e9dfd""
                    ]
                },
                "rulelist-id": "66f9746e-ad49-4a6f-a3fe-625b63e159f0",
                "nsappliances": [
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "7bc20e80-9af0-11e2-9e96-0800200c9a66",
                                "config-id": "9eba8119-2d0a-4210-bc26-9d3bad77e10f"
                            }
                        ]
                        
                    },
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "519a2b28-6a10-4833-abbe-51f0f149fb6f",
                                "config-id": "f62d5aed-7014-49d8-8fab-8a427c9592b5"
                            }
                        ]
                    },
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "3773d164-0b96-4c68-8c22-9642d55cc7b3",
                                "config-id": "7ef1fa64-9376-472b-99d9-31b2a4591acd"
                            }
                        ]
                        
                    }
                ]
            }

    



#####5.5  Delete a transparent NS Appliance Chain

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>DELETE </td><td>/nsappliances/transparentchains/id </td><td> Delete a specified Network Service Appliance Transparent Chain</td>
    </tr>
</table>

Normal Response Code(s): 204

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404), itemInUse (409)

This operation deletes a specified Network Service Transparent Chain from the system.

Specify the ID for the Network Service Appliance Transparent Chain as id in the URI.

This operation does not require a request body or return a response body

Implementation must terminate the NS Appliances created as part of this Chain, delete the OVS data flow entries and the ports created for this purpose.





##6.0  NS Routed Chain Management

#####6.1  List all routed NS Appliance Chain

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>GET </td><td> /nsapplainces/routedchains </td><td>List all NS Appliance Routed Chains</td>
    </tr>
</table>

Normal Response Code(s): 200, 203

Error Response Codes(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413)

*Example JSON response*

    {
        "routedchains": [
            {
                "id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                "name": "a routed chain",
 
                "net-info": {
                    "networks": [
                        {
                            "network-id": "3f8692d1-61aa-42ca-8967-fde1a5d0f084",
                            "subnet-id": "c4e52762-f445-4591-9d9e-97e10003847a"
                        },
                        {
                            "network-id": "cb302dcb-3375-410d-8ca2-8b7e07d2b6dd",
                            "subnet-id": "0161d804-1054-4dd1-8711-b85775ac5812"
                        }
                    ],
                    "internal-subnetid": "cb302dcb-3375-410d-8ca2-8b7e07d2b6dd"
                },
                "rulelist-id" : "5241c37f-25b5-4d92-bb3c-a66b2c112789",
                "nsappliances": [
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "940e2cdf-5173-475c-90b1-795590235119",
                                "config-id": "84182baf-a342-4951-821c-aba23d6d73d9"
                            }
                        ]
                        
                    },
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "1eaa45eb-43e3-467a-a10b-14a8bcdea1b7",
                                "config-id": "024d863b-6deb-4f76-8351-c61c0b1cd99d"
                            }
                        ]
                        
                    }

                ]
            },
            {
                "id": "e84eb701-ccbf-42f3-82ff-80d83e38e1bb",
                "name": "a second routed chain",
 
                "net-info": {
                    "networks": [
                        {
                            "network-id": "f83eefb3-0c76-4083-978b-268db09f7a61",
                            "subnet-id": "f37510be-0ad0-4589-a3cb-1a8894d0938d"
                        },
                        {
                            "network-id": "cb302dcb-3375-410d-8ca2-8b7e07d2b6dd",
                            "subnet-id": "0161d804-1054-4dd1-8711-b85775ac5812"
                        }
                    ],
                    "internal-subnetid": "cb302dcb-3375-410d-8ca2-8b7e07d2b6dd"
                },
                "rulelist-id" : "5241c37f-25b5-4d92-bb3c-a66b2c112789",
                "nsappliances": [
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "f8d79ffd-510c-4d53-aec5-9cec78f3623c",
                                "config-id": "42fb05ff-a626-4078-a393-ef4eceb6d33f"
                            }
                        ]
                        
                    }
                ]
            }
        ]
    }




#####6.2  create a routed NS Appliance Chain

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>POST </td><td> /nsapplainces/routedchains </td><td>Create a NS Appliance Routed Chains</td>
    </tr>
</table>

The following table describes the required and optional attributes that you can specify in the request body.

<table cellspacing = 30  >
    <tr>
        <th>Name</th><th>Description</th><th>Required</th>
    </tr>
    <tr>
        <td>name</td><td>Name of the routed chain </td><td>False</td>
    </tr>
    <tr>
        <td>networks</td><td> Provide a set of networks for which the network services are required</td><td>Yes</td>
    </tr>
    <tr>
        <td>ruelist-id</td><td>List of network rules for setting up action bypass</td><td>Yes</td>
    </tr>

    <tr>
        <td>internal-subnetid</td><td> Subnet id to be used for creating internal networks</td><td>Yes</td>
    </tr>
    <tr>
        <td>imagemap-id</td><td> Image to be used for the appliance</td><td>Yes</td>
    </tr>
    <tr>
    <tr>
        <td>configs</td><td> NS Appliance Configuration list for each network function of the appliance </td><td>Yes</td>
    </tr>
        <td>max-instances</td><td> number of appliances in the cluster </td><td>Yes</td>
    </tr>
    <tr>
        <td>flavorref</td><td>Flavor to use for the appliance. Overwrites the default flavor set in the image map </td><td>Yes</td>
    </tr>
    <tr>
        <td>metadata</td><td> metadata to pass to the appliance </td><td>Yes</td>
    </tr>
    <tr>
        <td>personality</td><td>personality files to inject to the appliance </td><td>Yes</td>
    </tr>
</table>

Implementation creates a chain of Network appliances between the networks configured. It uses the internal subnet-id to create intermediate subnets needed for L3 routing of the packets.


*Example JSON Request*


            {
                "name": "a second routed chain",
                "net-info": {
                    "networks": [
                        {
                            "network-id": "f83eefb3-0c76-4083-978b-268db09f7a61",
                            "subnet-id": "f37510be-0ad0-4589-a3cb-1a8894d0938d"
                        },
                        {
                            "network-id": "cb302dcb-3375-410d-8ca2-8b7e07d2b6dd",
                            "subnet-id": "0161d804-1054-4dd1-8711-b85775ac5812"
                        }
                    ],
                    "internal-subnetid": "cb302dcb-3375-410d-8ca2-8b7e07d2b6dd"
                },
                "rulelist-id" : "5241c37f-25b5-4d92-bb3c-a66b2c112789",
                "nsappliances": [
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "f8d79ffd-510c-4d53-aec5-9cec78f3623c",
                                "config-id": "42fb05ff-a626-4078-a393-ef4eceb6d33f"
                            }
                        ]
                        
                    }
                ]
            }

*Example JSON Response*

            {
                "id": "e84eb701-ccbf-42f3-82ff-80d83e38e1bb",
                "name": "a second routed chain",
                "net-info": {
                    "networks": [
                        {
                            "network-id": "f83eefb3-0c76-4083-978b-268db09f7a61",
                            "subnet-id": "f37510be-0ad0-4589-a3cb-1a8894d0938d"
                        },
                        {
                            "network-id": "cb302dcb-3375-410d-8ca2-8b7e07d2b6dd",
                            "subnet-id": "0161d804-1054-4dd1-8711-b85775ac5812"
                        }
                    ],
                    "internal-subnetid": "cb302dcb-3375-410d-8ca2-8b7e07d2b6dd"
                },
                "rulelist-id" : "5241c37f-25b5-4d92-bb3c-a66b2c112789",
                "nsappliances": [
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "f8d79ffd-510c-4d53-aec5-9cec78f3623c",
                                "config-id": "42fb05ff-a626-4078-a393-ef4eceb6d33f"
                            }
                        ]
                        
                    }
                ]
            }




#####3.7.3  Get details of routed NS Appliance Chain

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>GET </td><td>/nsappliances/routedchains/{chain_id} </td><td> List details of a specified Routed NS Appliance Chain</td>
    </tr>
</table>

Normal Response Code(s): 200, 203

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404)

Specify the Network Service Appliance Routed Chain ID as id in the URI.

This operation does not require a request body.

This operation returns the details of a specific Network Service Appliance Routed Chain by its ID.

*Example JSON response*

            {
                "id": "e84eb701-ccbf-42f3-82ff-80d83e38e1bb",
                "name": "a second routed chain",
                "net-info": {
                    "networks": [
                        {
                            "network-id": "f83eefb3-0c76-4083-978b-268db09f7a61",
                            "subnet-id": "f37510be-0ad0-4589-a3cb-1a8894d0938d"
                        },
                        {
                            "network-id": "cb302dcb-3375-410d-8ca2-8b7e07d2b6dd",
                            "subnet-id": "0161d804-1054-4dd1-8711-b85775ac5812"
                        }
                    ],
                    "internal-subnetid": "cb302dcb-3375-410d-8ca2-8b7e07d2b6dd"
                },
                "rulelist-id" : "5241c37f-25b5-4d92-bb3c-a66b2c112789",
                "nsappliances": [
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "f8d79ffd-510c-4d53-aec5-9cec78f3623c",
                                "config-id": "42fb05ff-a626-4078-a393-ef4eceb6d33f"
                            }
                        ]
                        
                    }
                ]
            }


#####6.4  Update a routed NS Appliance Chain

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>PUT </td><td>/nsappliances/routedchains/{id} </td><td> Update a specified NS Appliance Routed Chain</td>
    </tr>
</table>

Normal Response Code(s): 200

Error Response Code(s): computeFault (400, 500, Ã¢â‚¬Â¦), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404)

This operation enables you to update the editable attributes of a specified NS Appliance Routed Chain

Specify the Network Service Appliance Routed Chain ID as id in the URI.

The following table describes the attributes that you can specify in the request body:

<table cellspacing = 30  >
    <tr>
        <th>Name</th><th>Description</th>
    </tr>
    <tr>
        <td>name </td><td>You can change the NS Appliances Chain name </td></td><td>False</td>
    </tr>
    <tr>
        <td>networks</td><td>Change the network-ids that should have this chain</td></td><td>False</td>
    </tr>
    <tr>
        <td>rulelist-id</td><td>Change the rule list</td></td><td>False</td>
    </tr>
    <tr>
        <td>subnets</td><td>Change the subnet-ids that should have this chain</td></td><td>False</td>
    </tr>
    <tr>
        <td>internal-subnet</td><td>Change the internalsubnet-id that this chain use</td><td>False</td>
    </tr>
    <tr>
        <td>imagemap-id</td><td> NS Appliance image map id to use for the Appliance </td><td>False</td>
    </tr>
    <tr>
        <td>configs</td><td> NS Appliance Configuration list for each network function of the appliance </td><td>Yes</td>
    </tr>
    <tr>
        <td>max-instaces</td><td> number of instances to run per appliance cluster. If not specified, default value is 1 </td><td>No</td>
    </tr>
    <tr>
        <td>flavorref</td> Flavor to use for the NS Appliance. If not specified the default values specified in image map are taken <td></td><td>No</td>
    </tr>
    <tr>
        <td>metadata </td><td> Metadata to supply to the NS Appliance instance. Default content overwritten if provided</td><td>No</td>
    </tr>
    <tr>
        <td>personality</td><td>Personality files to inject to NS Appliance instance. Default content overwritten if provided </td><td>No</td>
    </tr>
</table>

When network-ids gets changed, the implementation must terminate the NS Appliances for the old networks and create the NS Appliance chain between
the new networks.

*Update NS Routed Chain JSON Request*

           {
                "id": "e84eb701-ccbf-42f3-82ff-80d83e38e1bb",
                "name": "a custom routed chain",
                "rulelist-id" : "9241c37f-25b5-4d92-bb3c-a66b2c112789"
     
            }

    
*Update NS Routed Chain JSON Response*

            {
                "id": "e84eb701-ccbf-42f3-82ff-80d83e38e1bb",
                "name": "a second routed chain",
                "net-info": {
                    "networks": [
                        {
                            "network-id": "f83eefb3-0c76-4083-978b-268db09f7a61",
                            "subnet-id": "f37510be-0ad0-4589-a3cb-1a8894d0938d"
                        },
                        {
                            "network-id": "cb302dcb-3375-410d-8ca2-8b7e07d2b6dd",
                            "subnet-id": "0161d804-1054-4dd1-8711-b85775ac5812"
                        }
                    ],
                    "internal-subnetid": "cb302dcb-3375-410d-8ca2-8b7e07d2b6dd"
                },
                "rulelist-id" : "9241c37f-25b5-4d92-bb3c-a66b2c112789",
                "nsappliances": [
                    {
                        "imagemap-id": "36b63baa-8010-4873-b040-1d886e39fd8b",
                        "max-instances":1,
                        "configs": [
                            {
                                "networkfunction-id": "f8d79ffd-510c-4d53-aec5-9cec78f3623c",
                                "config-id": "42fb05ff-a626-4078-a393-ef4eceb6d33f"
                            }
                        ]
                        
                    }
                ]
            }







#####6.5  Delete a routed NS Appliance Chain

<table cellspacing = 30  >
    <tr>
        <th>Verb</th><th>URI</th><th>Description</th>
    </tr>
    <tr>
        <td>DELETE </td><td>/nsappliances/routedchains/id </td><td> Delete a specified Network Service Appliance Routed Chain</td>
    </tr>
</table>

Normal Response Code(s): 204

Error Response Code(s): computeFault (400, 500), serviceUnavailable (503), unauthorized (401), forbidden (403), badRequest (400), badMethod (405), overLimit (413), itemNotFound (404), itemInUse (409)

This operation deletes a specified Network Service Routed Chain from the system.

Specify the ID for the Network Service Appliance Routed Chain as id in the URI.

This operation does not require a request body or return a response body

Implementation must terminate the NS Appliances created as part of this Chain, delete the OVS data flow entries and the ports created for this purpose and then terminate the networks.



