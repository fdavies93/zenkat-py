# Zenkat Data Pipeline

This is a technical description of the Zenkat data pipeline. It's designed for reading by developers / people who are interested. Most people are unlikely to care about this.

## 1: Index

The first step is to load an index of all documents in the path. This could be loaded from a cache, or not; it doesn't really matter. In any case what's important is that data is loaded, then turned into a bunch of fields that can be queried.

## 2: Query

This step is where the data we're interested in for a given result is retrieved. E.g. `list pages` retrieves pages.

It outputs an array of objects which are passed into the next command.

## 3: Data Shaping

This is all the features that make Zenkat actually useful, like filtering, sorting, limit, group, etc.

It outputs an array of objects (which may or may not be of the same form as the originals).

## 4: Formatting / Output

This transforms the objects received from 3 into an array of new objects for output. For console output, this is an intermediate step which lets users decide their own formatting.

### 5: Rendering

In the previous step we took our final object and rendered it to a format used only for formatting. In this step we render out our object. We can use the same syntax as for accessing fields to access properties, but we 

## Example: Tasks (console output)

1. All documents are indexed and ListItems are extracted as a field of the Page object.
2. We query the Page object to retrieve ListItems with the type 'task' by traversing the node tree of ListItems. These ListItems are returned as an object containing information about ListItems and the page.
3. We apply filters and sort methods to ListItems. Some of these may apply recursively, but the generic methods should be written such that using them on one item or on several doesn't matter.
4. The ListItems are converted into a *flat* list of objects for rendering.
5. The format string is applied over the new object and the parts of the resulting query are assembled and printed out.