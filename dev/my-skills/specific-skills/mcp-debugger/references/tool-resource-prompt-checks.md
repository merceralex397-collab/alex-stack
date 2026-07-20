# Tools, Resources, and Prompts

Use this reference when the server starts but MCP features are missing, malformed, or failing at runtime. For lifecycle/capability errors (`-32602`) and transport issues see `protocol-and-transport.md`.

## Schema and error conventions (2025-11-25)

- JSON Schema **2020-12** is the default dialect for tool input/output schemas. A schema
  written for an older dialect can cause `-32602`/validation mismatches.
- Return tool **input-validation** failures as Tool Execution Errors (an `isError` result),
  not JSON-RPC protocol errors, so the model can read the message and self-correct. Reserve
  protocol-level `-32602` for genuine capability/parameter-shape mismatches.

## Tools

Check registration:

- Tool registration code runs during startup.
- Tool names are stable and valid for the target clients.
- Descriptions explain when to use the tool and what arguments mean.
- Input schema is valid JSON Schema and matches handler expectations.
- Required fields are truly required by the handler.

Check invocation:

- Compare the actual arguments sent by the client with Inspector arguments.
- Avoid unsupported values such as `undefined`, `NaN`, functions, class instances, or circular objects.
- Validate optional fields and defaults explicitly.
- Log request ID, tool name, argument summary, latency, upstream status, and error class.
- Return tool errors as MCP tool results when the server should stay alive.
- Throw process-level errors only for fatal startup or infrastructure failures.

Check result shape:

- Return valid MCP content blocks.
- If using structured content, match the advertised output schema.
- Keep large payloads bounded or provide resources instead.
- Sanitize sensitive data from returned error text.

## Resources

Check:

- `resources/list` returns expected resources.
- `resources/read` works for each URI shape.
- Resource URIs are deterministic and documented.
- Resource templates expand correctly.
- MIME types match returned content.
- File resources respect client roots, server allowlists, and filesystem permissions.
- Subscriptions emit updates only when supported and expected.

## Prompts

Check:

- Prompt names are stable.
- Descriptions distinguish similar prompts.
- Argument schemas match generated message logic.
- Missing required and optional arguments are handled cleanly.
- Generated messages use valid roles and content blocks.

## Edge Cases

Exercise these in Inspector:

- Missing required arguments.
- Invalid argument types.
- Empty strings, arrays, and objects.
- Permission denied.
- Upstream API timeout.
- Upstream 401/403/429/500.
- Concurrent calls if the server shares mutable state.
- Large results and slow responses.
