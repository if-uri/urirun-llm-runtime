
# URIRUN LLM Runtime — OpenAPI Runtime Spec

openapi: 3.0.3
info:
	title: urirun LLM Runtime API
	version: '0.1.0'
	description: |
		Canonical runtime contract for executing URI processes in the ifURI ecosystem.
		LLMs should target this API when generating code that performs external actions
		(kvm://, app://, shell://, work://, etc.).

servers:
	- url: http://{host}:{port}
		variables:
			host:
				default: localhost
			port:
				default: '8765'

paths:
	/run:
		post:
			summary: Execute a URI process
			description: |
				Execute a single atomic URI step on the node. The runtime interprets the
				scheme and path (query vs command) and returns a JSON result object.
			requestBody:
				required: true
				content:
					application/json:
						schema:
							$ref: '#/components/schemas/RunRequest'
			responses:
				'200':
					description: Execution result
					content:
						application/json:
							schema:
								$ref: '#/components/schemas/RunResponse'
				'4XX':
					description: Client error
				'5XX':
					description: Server error

components:
	schemas:
		RunRequest:
			type: object
			required: [uri]
			properties:
				uri:
					type: string
					description: The URI to execute, e.g. kvm://laptop/diag/query/which
					example: kvm://laptop/diag/query/which
				payload:
					type: object
					additionalProperties: true
					description: Optional payload for the URI
		RunResponse:
			type: object
			properties:
				ok:
					type: boolean
					description: Success indicator
				action:
					type: string
					description: Per-scheme action (e.g. capture, type, focus)
				via:
					type: string
					description: Which backend was used (rfb, portal, wtype, ydotool)
				result:
					type: object
					additionalProperties: true
				error:
					type: string
					description: Error string on failure

security:
	- bearerAuth: []

components:
	securitySchemes:
		bearerAuth:
			type: http
			scheme: bearer
			bearerFormat: JWT

examples:
	kvm_diag:
		summary: KVM diagnostic query
		value:
			uri: kvm://laptop/diag/query/which
			payload: {}

	shell_date:
		summary: Run date via shell://
		value:
			uri: shell://laptop/command/date
			payload: {}

notes:
	- The runtime MUST document scheme semantics externally (this OpenAPI file
		defines the transport and core shapes only).
	- Clients MAY set `Authorization: Bearer <TOKEN>` when the node requires auth.

