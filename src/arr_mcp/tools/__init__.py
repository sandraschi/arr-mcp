"""Tool package — portmanteau tool modules.

Each arr gets its own module with a ``register_*_tools(mcp, client)`` function.
Importing sub-modules here triggers ``@mcp.tool()`` decorator registration.
"""
