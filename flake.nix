 {
  description = "python venv for anthropic mcp";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = nixpkgs.legacyPackages."${system}";
      in
        rec {
          devShell = pkgs.mkShell {
            nativeBuildInputs = with pkgs; [
              python312Packages.python
              python312Packages.python-lsp-server
              python312Packages.autopep8
              uv
              nodejs_20
            ];

            shellHook = ''
                export GITSTATUS_LOG_LEVEL=DEBUG;
                export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib.outPath}/lib:$LD_LIBRARY_PATH";

                # Check if .venv directory exists
                if [ ! -d ".venv" ]; then
                  echo "Creating virtual environment with uv..."
                  uv venv
                fi

                # Activate the virtual environment if it exists
                if [ -d ".venv" ]; then
                  echo "Activating virtual environment..."
                  source .venv/bin/activate
                fi

                exec zsh
              '';
          };
        }
    );
} 

