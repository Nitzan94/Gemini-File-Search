# Metadata Filtering

How to organize and filter documents using custom metadata.

## What is Metadata?

Think of metadata as **labels on file folders**:

**Without metadata:**
- All files mixed together in one big pile
- Search through everything every time
- Slow and returns irrelevant results

**With metadata:**
- Files organized by labels: department, year, project, status
- Search only relevant labeled folders
- Fast and returns exactly what you need

## Why Use Metadata?

### Real-World Scenario

You have 500 documents in your store:
- 200 financial reports (2020-2024)
- 150 technical specifications
- 100 meeting notes
- 50 legal contracts

**Question:** "What was Q2 revenue?"

**Without metadata filtering:**
- Searches all 500 documents
- Takes longer
- Might return revenue from wrong year or department

**With metadata filtering:**
```python
metadata_filter='department=Finance AND year=2024 AND quarter=Q2'
```
- Searches only 10 relevant Q2 2024 financial reports
- Much faster
- Always correct year and department

## Adding Metadata to Documents

### When Uploading

```python
operation = client.file_search_stores.upload_to_file_search_store(
    file='Q2_Report.pdf',
    file_search_store_name=store.name,
    config={
        'display_name': 'Q2 Financial Report',
        'custom_metadata': [
            {'key': 'department', 'string_value': 'Finance'},
            {'key': 'year', 'string_value': '2024'},
            {'key': 'quarter', 'string_value': 'Q2'},
            {'key': 'category', 'string_value': 'financial'},
            {'key': 'status', 'string_value': 'final'},
            {'key': 'author', 'string_value': 'Jane Smith'}
        ]
    }
)
```

**What this code does:**
- Uploads Q2 report with 6 metadata labels attached
- Each label is a key-value pair (department=Finance, year=2024, etc.)
- These labels let you filter searches later
- Think: filing a document with multiple colored stickers for easy finding
- Later can search "only Finance, Q2, 2024, final documents"

### Metadata Limits

- **Max 20 key-value pairs** per document
- Keys and values are **case-sensitive**
- Only **string values** supported
- Keys must be valid identifiers (letters, numbers, underscores)

## Filtering Syntax

Gemini uses **AIP-160** filter syntax (Google's standard).

### Basic Filters

#### Single Condition

```python
# Only Finance documents
metadata_filter='department=Finance'

# Only 2024 documents
metadata_filter='year=2024'

# Only final status
metadata_filter='status=final'
```

**What this code does:**
- First example: Search only Finance department documents
- Second example: Search only 2024 documents
- Third example: Search only final (not draft) documents
- Single condition filters - simplest type
- Like looking in one specific file drawer

#### AND Operator

```python
# Finance documents from 2024
metadata_filter='department=Finance AND year=2024'

# Q2 financial reports that are final
metadata_filter='quarter=Q2 AND category=financial AND status=final'
```

**What this code does:**
- AND means "must match ALL conditions"
- First: document must be Finance AND 2024 (both required)
- Second: document must be Q2 AND financial AND final (all 3 required)
- Narrows search - fewer results but more specific
- Like "file drawer A AND folder B" - very specific location

#### OR Operator

```python
# Finance or HR documents
metadata_filter='department=Finance OR department=HR'

# Q1 or Q2 documents
metadata_filter='quarter=Q1 OR quarter=Q2'
```

**What this code does:**
- OR means "match ANY condition"
- First: document can be Finance OR HR (either one works)
- Second: document can be Q1 OR Q2 (either quarter)
- Broadens search - more results
- Like "look in drawer A OR drawer B" - multiple locations

#### NOT Operator

```python
# Not draft documents
metadata_filter='status!=draft'

# Everything except Engineering
metadata_filter='department!=Engineering'
```

**What this code does:**
- != means "NOT equal to" (exclude)
- First: Get all documents EXCEPT drafts (finals, archived, etc.)
- Second: Get all departments EXCEPT Engineering
- Exclusion filter - removes unwanted results
- Like "search everywhere EXCEPT this drawer"

### Complex Filters

#### Combining AND, OR, NOT

```python
# Finance OR HR, but only from 2024
metadata_filter='(department=Finance OR department=HR) AND year=2024'

# Q2 or Q3, but not drafts
metadata_filter='(quarter=Q2 OR quarter=Q3) AND status!=draft'
```

**What this code does:**
- Parentheses group conditions (like math)
- First: (Finance OR HR) then narrow to 2024 only
- Second: (Q2 OR Q3) then exclude drafts
- Complex logic: multiple conditions combined
- Like "drawer A or B, but only 2024 folders, and not drafts"

#### Multiple Conditions

```python
# Technical or financial docs from 2024, not archived
metadata_filter='''
    (category=technical OR category=financial)
    AND year=2024
    AND status!=archived
'''
```

## Common Metadata Patterns

### Pattern 1: Department & Date

```python
# Upload with metadata
custom_metadata = [
    {'key': 'department', 'string_value': 'Engineering'},
    {'key': 'year', 'string_value': '2024'},
    {'key': 'month', 'string_value': '06'}
]

# Query Engineering docs from June 2024
metadata_filter='department=Engineering AND year=2024 AND month=06'
```

**What this code does:**
- First part: Defines metadata structure (department, year, month)
- Second part: Searches using that exact structure
- Filters to Engineering + 2024 + June (very specific timeframe)
- Good for: Companies with many departments needing time-based searches
- Result: Only June 2024 Engineering documents

**Use case:** Large organization with multiple departments

### Pattern 2: Project & Status

```python
# Upload with metadata
custom_metadata = [
    {'key': 'project', 'string_value': 'Alpha'},
    {'key': 'status', 'string_value': 'active'},
    {'key': 'priority', 'string_value': 'high'}
]

# Query active, high-priority Alpha project docs
metadata_filter='project=Alpha AND status=active AND priority=high'
```

**What this code does:**
- Metadata structure: project name, status, priority
- Search filter: only active, high-priority Alpha docs
- Excludes completed/archived Alpha docs and low-priority items
- Perfect for: Project tracking where priority and status matter
- Result: Urgent items needing attention on Project Alpha

**Use case:** Project management system

### Pattern 3: Content Type & Confidentiality

```python
# Upload with metadata
custom_metadata = [
    {'key': 'type', 'string_value': 'contract'},
    {'key': 'confidential', 'string_value': 'yes'},
    {'key': 'retention', 'string_value': '7years'}
]

# Query confidential contracts
metadata_filter='type=contract AND confidential=yes'
```

**What this code does:**
- Metadata for legal docs: type, confidentiality level, retention period
- Filter searches: only confidential contracts
- Excludes non-confidential contracts and non-contract docs
- Use case: Legal teams managing sensitive documents
- Result: Only high-security contracts that need careful handling

**Use case:** Legal document management

### Pattern 4: Customer & Product

```python
# Upload with metadata
custom_metadata = [
    {'key': 'customer', 'string_value': 'Acme Corp'},
    {'key': 'product', 'string_value': 'Enterprise Plan'},
    {'key': 'category', 'string_value': 'support_ticket'}
]

# Query Acme Corp support tickets for Enterprise Plan
metadata_filter='customer=Acme Corp AND product=Enterprise Plan AND category=support_ticket'
```

**What this code does:**
- Metadata for support: customer name, product, document category
- Filter searches: Acme Corp + Enterprise Plan + support tickets only
- Excludes other customers, other products, non-ticket docs
- Perfect for: Support teams looking up customer-specific issues
- Result: All support tickets for Acme Corp's Enterprise Plan

**Use case:** Customer support system

## Querying with Filters

### Basic Query with Filter

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What was the total revenue?',
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[store.name],
                metadata_filter='department=Finance AND year=2024'
            )
        )]
    )
)

print(response.text)
```

**What this code does:**
- Asks "What was total revenue?" but pre-filters to Finance + 2024 only
- metadata_filter runs BEFORE semantic search begins
- Only searches Finance 2024 documents, ignores everything else
- Gets AI-generated answer from filtered documents
- Prints the answer
- Result: Revenue answer guaranteed to be from Finance dept, 2024

### Dynamic Filters Based on User Input

```python
def query_with_filter(question, department, year):
    """Query documents with dynamic metadata filter"""
    metadata_filter = f'department={department} AND year={year}'

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=question,
        config=types.GenerateContentConfig(
            tools=[types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[store.name],
                    metadata_filter=metadata_filter
                )
            )]
        )
    )

    return response.text

# Use it
answer = query_with_filter(
    question='What was Q2 revenue?',
    department='Finance',
    year='2024'
)
```

**What this code does:**
- Creates reusable function that builds filter from parameters
- Takes question + department + year as inputs
- Builds filter string dynamically (department=X AND year=Y)
- Queries with that filter
- Returns answer text
- Example usage: asks about Q2 revenue in Finance 2024 documents
- Benefit: Change department/year without rewriting query code

### Query Multiple Departments

```python
metadata_filter='department=Finance OR department=Sales OR department=Marketing'

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What were the key highlights this quarter?',
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[store.name],
                metadata_filter=metadata_filter
            )
        )]
    )
)
```

**What this code does:**
- Searches across 3 departments simultaneously (Finance, Sales, Marketing)
- OR means "include any of these departments"
- Asks for quarterly highlights across all 3 departments
- Result: Combined insights from Finance + Sales + Marketing
- Good for: Executive reports that need cross-department view

## Metadata Strategy

### Good Metadata Design

**Do:**
- Use consistent naming: `department=Finance` (not `dept`, `Department`, `DEPARTMENT`)
- Use predictable values: `status=draft` | `final` | `archived` (clear states)
- Keep it simple: `year=2024` (not `year=FY2024` or `year=fiscal_year_2024`)
- Plan ahead: Design metadata schema before mass upload

**Don't:**
- Mix formats: `date=2024-06-15` and `date=June 15, 2024`
- Use spaces in keys: `project name=Alpha` (use `project_name=Alpha`)
- Overuse: Don't add 20 metadata fields "just in case"
- Forget case: `Department=Finance` ≠ `department=Finance`

### Example Metadata Schema

For a company document management system:

```python
METADATA_SCHEMA = {
    'department': ['Finance', 'Engineering', 'HR', 'Legal', 'Sales'],
    'year': ['2024', '2023', '2022'],
    'quarter': ['Q1', 'Q2', 'Q3', 'Q4'],
    'category': ['financial', 'technical', 'legal', 'marketing'],
    'status': ['draft', 'review', 'final', 'archived'],
    'confidential': ['yes', 'no'],
    'author': ['string'],  # Free-form
    'project': ['string']   # Free-form
}

def add_document_metadata(file, department, year, quarter, category, status):
    """Upload with validated metadata"""
    return client.file_search_stores.upload_to_file_search_store(
        file=file,
        file_search_store_name=store.name,
        config={
            'custom_metadata': [
                {'key': 'department', 'string_value': department},
                {'key': 'year', 'string_value': year},
                {'key': 'quarter', 'string_value': quarter},
                {'key': 'category', 'string_value': category},
                {'key': 'status', 'string_value': status}
            ]
        }
    )
```

**What this code does:**
- First part: Defines company-wide metadata standard (schema)
- Lists allowed values for each field (Finance/HR/Legal for department, etc.)
- Ensures consistency - everyone uses same labels
- Second part: Helper function for uploading with standard metadata
- Takes file + metadata values, uploads with proper structure
- Prevents typos and maintains consistency across all uploads
- Think: Company-wide filing system with standard label colors

## Performance Benefits

### Scenario: 1000 Documents

**Without filtering:**
- Query searches all 1000 documents
- Takes 3-5 seconds
- Returns results from all departments/years

**With filtering (to 50 documents):**
- Query searches only 50 relevant documents
- Takes <1 second
- Returns only relevant results

**Speed improvement: 3-5x faster**

### When to Use Filters

**Always use filters when:**
- You have >100 documents
- Documents span multiple categories/departments/years
- Query performance matters
- You want precise results

**Filters optional when:**
- You have <50 documents
- All documents are similar topic
- You want broad search

## Real-World Examples

### Example 1: Customer Support System

```python
# Upload customer support tickets
for ticket in tickets:
    operation = client.file_search_stores.upload_to_file_search_store(
        file=ticket.file,
        file_search_store_name=store.name,
        config={
            'display_name': ticket.title,
            'custom_metadata': [
                {'key': 'customer', 'string_value': ticket.customer_name},
                {'key': 'product', 'string_value': ticket.product},
                {'key': 'priority', 'string_value': ticket.priority},
                {'key': 'status', 'string_value': ticket.status},
                {'key': 'category', 'string_value': ticket.category}
            ]
        }
    )

# Query: Find all high-priority open tickets for Acme Corp
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Summarize all open issues',
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[store.name],
                metadata_filter='customer=Acme Corp AND priority=high AND status=open'
            )
        )]
    )
)
```

**What this code does:**
- Upload phase: Loops through support tickets, uploads each with 5 metadata fields
- Metadata captures: customer, product, priority, status, category
- Query phase: Searches for Acme Corp + high priority + open status only
- Ignores: closed tickets, other customers, low priority items
- Gets AI summary of only urgent open Acme Corp issues
- Perfect for: Support teams triaging customer problems

### Example 2: Legal Document Search

```python
# Upload contracts
for contract in contracts:
    operation = client.file_search_stores.upload_to_file_search_store(
        file=contract.file,
        file_search_store_name=store.name,
        config={
            'display_name': contract.title,
            'custom_metadata': [
                {'key': 'type', 'string_value': 'contract'},
                {'key': 'party', 'string_value': contract.counterparty},
                {'key': 'year', 'string_value': str(contract.year)},
                {'key': 'status', 'string_value': contract.status},
                {'key': 'value', 'string_value': contract.value_tier}
            ]
        }
    )

# Query: Find all active contracts over $1M from 2024
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What are the key terms?',
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[store.name],
                metadata_filter='type=contract AND status=active AND year=2024 AND value=high'
            )
        )]
    )
)
```

**What this code does:**
- Upload: Loops through contracts, uploads with legal metadata
- Metadata: type, counterparty, year, status, value tier (high/medium/low)
- Query: Filters to contract + active + 2024 + high value only
- Ignores: expired contracts, low value, old years
- Gets AI analysis of key terms in major active 2024 contracts
- Use case: Legal teams reviewing high-value active agreements

### Example 3: Research Paper Library

```python
# Upload research papers
for paper in papers:
    operation = client.file_search_stores.upload_to_file_search_store(
        file=paper.pdf,
        file_search_store_name=store.name,
        config={
            'display_name': paper.title,
            'custom_metadata': [
                {'key': 'author', 'string_value': paper.author},
                {'key': 'year', 'string_value': str(paper.year)},
                {'key': 'field', 'string_value': paper.field},
                {'key': 'peer_reviewed', 'string_value': 'yes' if paper.peer_reviewed else 'no'},
                {'key': 'cited_count', 'string_value': paper.citation_tier}
            ]
        }
    )

# Query: Find highly-cited peer-reviewed ML papers from 2023-2024
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What are recent breakthroughs in neural architecture search?',
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[store.name],
                metadata_filter='field=machine_learning AND peer_reviewed=yes AND (year=2023 OR year=2024) AND cited_count=high'
            )
        )]
    )
)
```

**What this code does:**
- Upload: Academic papers with research metadata
- Metadata: author, year, field, peer review status, citation tier
- Query: Filters to ML + peer reviewed + 2023/2024 + highly cited
- Excludes: non-peer-reviewed, old papers, low citations, other fields
- Asks about neural architecture breakthroughs in recent high-quality papers
- Perfect for: Researchers doing literature reviews on specific topics

## Troubleshooting

### Filter Returns No Results

**Possible causes:**
1. **Typo in filter** - Check key names match exactly (case-sensitive)
2. **No matching documents** - Verify documents exist with those metadata values
3. **Syntax error** - Check parentheses, AND/OR operators

**Debug:**
```python
# List all documents to see metadata
docs = client.file_search_stores.documents.list(parent=store.name)
for doc in docs:
    print(f'{doc.display_name}: {doc.custom_metadata}')
```

**What this code does:**
- Lists all documents in your store
- For each document, prints name + all metadata labels
- Helps debug: "Why isn't my filter working?"
- Shows exact metadata values (check spelling, case, etc.)
- Use when: Filter returns nothing and you're not sure why

### Filter Syntax Error

**Common mistakes:**

```python
# ❌ Wrong: Missing quotes
metadata_filter=department=Finance

# ✓ Right: Quoted values
metadata_filter='department=Finance'

# ❌ Wrong: Using == instead of =
metadata_filter='year==2024'

# ✓ Right: Single =
metadata_filter='year=2024'

# ❌ Wrong: Unbalanced parentheses
metadata_filter='(department=Finance AND year=2024'

# ✓ Right: Balanced
metadata_filter='(department=Finance AND year=2024)'
```

### Filter Too Restrictive

If you get no results, broaden the filter:

```python
# Too restrictive - might get no results
metadata_filter='department=Finance AND year=2024 AND quarter=Q2 AND status=final AND author=Jane Smith'

# Better - get more results
metadata_filter='department=Finance AND year=2024 AND quarter=Q2'
```

## Best Practices

1. **Design metadata schema upfront** - Consistent naming across all documents
2. **Use standard values** - Predefined lists (Finance, HR, Legal) not free-form
3. **Keep keys simple** - `year`, `department`, `status` (short, clear)
4. **Always filter by date** - Avoid returning outdated information
5. **Test filters first** - Verify filter returns expected documents before deploying
6. **Document your schema** - Team reference for metadata conventions
7. **Monitor filter performance** - Check if filters actually speed up queries
8. **Validate on upload** - Reject documents with invalid metadata values

## Key Takeaways

1. **Metadata = Organization** - Labels for finding documents quickly
2. **Filters = Speed** - Query only relevant documents (3-5x faster)
3. **AIP-160 syntax** - Google's standard filter language (AND, OR, NOT)
4. **Max 20 pairs** - Keep metadata focused and essential
5. **Case-sensitive** - `Department` ≠ `department`
6. **Plan ahead** - Design schema before mass upload
7. **Validate values** - Use predefined lists, not free-form
8. **Always use for large stores** - Essential for >100 documents

**Bottom line:** Metadata transforms unorganized document piles into structured, fast-searchable libraries.

## Next Steps

- [Upload Documents with Metadata →](./upload-documents)
- [Query with Filters →](./query)
- [Production Deployment →](./production-deployment)
- [Understanding Documents →](../concepts/documents)
