#!/bin/bash

# Browser-Use Remote Chromium Connection Solution - One-Click Build Script
# Function: Compile Go reverse proxy + Build E2B Template

set -e  # Exit immediately on error

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

source .env

# Output functions
log_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${PURPLE}🔧 $1${NC}"
}

# Check necessary tools
check_dependencies() {
    log_step "Checking build dependencies..."
    
    # Check Go
    if ! command -v go &> /dev/null; then
        log_error "Go is not installed or not in PATH"
        echo "Please install Go: https://golang.org/doc/install"
        exit 1
    fi
    log_success "Go is installed: $(go version)"
    
    # Check E2B CLI
    if ! command -v e2b &> /dev/null; then
        log_error "E2B CLI is not installed or not in PATH"
        echo "Please install E2B CLI: npm install -g @e2b/cli"
        exit 1
    fi
    log_success "E2B CLI is installed: $(e2b --version)"
    
    # Check key files
    if [[ ! -f "reverse-proxy.go" ]]; then
        log_error "reverse-proxy.go file does not exist"
        exit 1
    fi
    
    if [[ ! -f "e2b.Dockerfile" ]]; then
        log_error "e2b.Dockerfile file does not exist"
        exit 1
    fi
    
    if [[ ! -f "start-up.sh" ]]; then
        log_error "start-up.sh file does not exist"
        exit 1
    fi
    
    log_success "All necessary files exist"
}

# Compile Go reverse proxy
compile_proxy() {
    log_step "Compiling Go reverse proxy as Linux x86 binary file..."
    
    # Set compilation parameters
    export GOOS=linux
    export GOARCH=amd64
    export CGO_ENABLED=0
    
    # Compilation output file name
    OUTPUT_FILE="reverse-proxy"
    
    log_info "Compilation configuration:"
    echo "  Source file: reverse-proxy.go"
    echo "  Target file: $OUTPUT_FILE"
    echo "  Target system: $GOOS"
    echo "  Target architecture: $GOARCH"
    echo "  CGO: $CGO_ENABLED"
    
    # Start compilation
    if go build -ldflags="-s -w" -o "$OUTPUT_FILE" reverse-proxy.go; then
        log_success "Reverse proxy compilation successful!"
        
        # Display file information
        if [[ -f "$OUTPUT_FILE" ]]; then
            FILE_SIZE=$(ls -lh "$OUTPUT_FILE" | awk '{print $5}')
            log_info "Generated binary file: $OUTPUT_FILE ($FILE_SIZE)"
            
            # Verify file type
            FILE_TYPE=$(file "$OUTPUT_FILE")
            log_info "File type: $FILE_TYPE"
        fi
    else
        log_error "Reverse proxy compilation failed!"
        exit 1
    fi
}

# Build E2B Template
build_e2b_template() {
    log_step "Building E2B Template..."
    export E2B_DOMAIN=sandbox.novita.ai

    echo "E2B_DOMAIN: $E2B_DOMAIN"
    echo "E2B_API_KEY: $E2B_API_KEY"
    
    # Check if already logged into E2B
    if ! e2b auth info &> /dev/null; then
        log_warning "Not logged into E2B, please login first:"
        echo "  e2b auth login"
        exit 1
    fi
    
    # Execute build
    log_info "Starting to build E2B Template..."
    echo "Build command: e2b template build -c \"/app/.browser-use/start-up.sh\""
    echo ""
    
    if e2b template build -c "/app/.browser-use/start-up.sh"; then
        log_success "E2B Template build successful!"
    else
        log_error "E2B Template build failed!"
        log_warning "Common troubleshooting:"
        echo "  1. Check Dockerfile syntax"
        echo "  2. Check network connection"
        echo "  3. Ensure E2B account has sufficient permissions"
        echo "  4. View build logs for detailed error information"
        exit 1
    fi
}

# Display build results and usage instructions
show_usage() {
    log_success "🎉 Build completed!"
    echo ""
    echo -e "${BLUE}📋 Usage Instructions:${NC}"
    echo ""
    echo "1. Get Template ID (copy from build output above)"
    echo ""
    echo "2. Use in your Python code:"
    echo -e "${CYAN}"
    cat << 'EOF'
View demo example: https://gitlab.paigod.work/saiki/browser-use-template-demo
EOF
    echo -e "${NC}"
    echo ""
    echo -e "${BLUE}🔧 Debug Endpoints:${NC}"
    echo "  Health check: https://9223-your-sandbox-host/health"
    echo "  Performance metrics: https://9223-your-sandbox-host/metrics"
    echo ""
    echo -e "${GREEN}🚀 You can now start using browser-use for remote browser automation!${NC}"
}

# Main function
main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║         Browser-Use Remote Chromium Connection Solution ║"
    echo "║                  One-Click Build Script                ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    
    # Check current directory
    if [[ ! -f "reverse-proxy.go" ]] || [[ ! -f "e2b.Dockerfile" ]]; then
        log_error "Please run this script in the project root directory"
        exit 1
    fi
    
    # Execute build steps
    check_dependencies
    echo ""
    
    compile_proxy
    echo ""
    
    build_e2b_template
    echo ""
    
    show_usage
}

# Error handling
trap 'log_error "An error occurred during the build process, please check the error information above"' ERR

# Run main function
main "$@" 