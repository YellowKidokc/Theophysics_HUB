These engine folders point to NAS paths and were not linked automatically here because:

- UNC junctions are not supported
- symbolic links require administrator privileges in this session

Use `create_engine_links.cmd` from an elevated shell if you want real directory links.
