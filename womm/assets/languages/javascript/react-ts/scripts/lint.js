#!/usr/bin/env node
// ///////////////////////////////////////////////////////////////
// REACT-TS LINT - React (TypeScript) Project Linting Script
// ///////////////////////////////////////////////////////////////

/**
 * React (TypeScript) project linting script.
 *
 * This script automates code quality checks:
 * - ESLint for style and error detection (with React + TypeScript support)
 * - Prettier for formatting (with JSX support)
 * - TypeScript compiler (tsc) for type checking
 */

// ///////////////////////////////////////////////////////////////
// IMPORTS
// ///////////////////////////////////////////////////////////////
// Standard library imports
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// ///////////////////////////////////////////////////////////////
// SECURITY UTILITIES
// ///////////////////////////////////////////////////////////////

/**
 * Check if a file or directory is excluded for security reasons.
 *
 * @param {string} filePath - Path to check
 * @returns {boolean} True if path should be excluded for security reasons
 */
function isSecurityExcluded(filePath) {
  const securityPatterns = [
    '.env',
    '.secret',
    'password',
    'secret',
    '.key',
    '.pem',
    '.crt',
    'credentials',
    'keys',
  ];

  const lowerPath = filePath.toLowerCase();
  const fileName = path.basename(filePath).toLowerCase();

  return securityPatterns.some((pattern) => {
    return lowerPath.includes(pattern) || fileName.includes(pattern);
  });
}

// ///////////////////////////////////////////////////////////////
// PROJECT DETECTION
// ///////////////////////////////////////////////////////////////

/**
 * Detect React TypeScript directories while excluding sensitive files.
 *
 * @param {string} basePath - Base path to search from (default: current directory)
 * @returns {string[]} List of directory paths to analyze
 */
function detectProjectDirs(basePath = null) {
  const currentDir = basePath ? path.resolve(basePath) : process.cwd();
  const targetDirs = [];

  try {
    const items = fs.readdirSync(currentDir, { withFileTypes: true });

    // Search for directories with TypeScript/TSX files
    for (const item of items) {
      if (
        item.isDirectory() &&
        !item.name.startsWith('.') &&
        !['node_modules', 'dist', 'build', 'coverage', '.next'].includes(
          item.name
        ) &&
        !isSecurityExcluded(path.join(currentDir, item.name))
      ) {
        // Check if it contains TypeScript/TSX files
        let hasTsFiles = false;
        try {
          const tsFiles = fs
            .readdirSync(path.join(currentDir, item.name))
            .filter(
              (f) => f.endsWith('.ts') || f.endsWith('.tsx')
            );
          if (tsFiles.length > 0) {
            hasTsFiles = true;
          }
        } catch (err) {
          // Ignore file access errors
        }

        if (hasTsFiles) {
          targetDirs.push(item.name);
        }
      }
    }

    // Add 'src' if it exists and is not excluded
    const srcDir = path.join(currentDir, 'src');
    if (
      fs.existsSync(srcDir) &&
      fs.statSync(srcDir).isDirectory() &&
      !isSecurityExcluded(srcDir)
    ) {
      targetDirs.push('src');
    }

    // Fallback: analyze current directory if it contains safe TS files
    if (targetDirs.length === 0) {
      try {
        const files = fs.readdirSync(currentDir);
        const hasSafeTsFiles = files.some(
          (f) =>
            (f.endsWith('.ts') || f.endsWith('.tsx')) &&
            !isSecurityExcluded(path.join(currentDir, f))
        );
        if (hasSafeTsFiles) {
          targetDirs.push('.');
        }
      } catch (err) {
        // Ignore errors
      }
    }
  } catch (err) {
    console.error(`Error reading directory: ${err.message}`);
  }

  return targetDirs;
}

// ///////////////////////////////////////////////////////////////
// COMMAND EXECUTION UTILITIES
// ///////////////////////////////////////////////////////////////

/**
 * Check if a tool is available via npm scripts or npx.
 *
 * @param {string} toolName - Name of the tool
 * @returns {boolean} True if available
 */
function checkNpmTool(toolName) {
  try {
    // Check if package.json exists
    const packageJsonPath = path.join(process.cwd(), 'package.json');
    if (fs.existsSync(packageJsonPath)) {
      const packageJson = JSON.parse(
        fs.readFileSync(packageJsonPath, 'utf-8')
      );
      // Check if tool is in devDependencies or dependencies
      const deps = {
        ...packageJson.dependencies,
        ...packageJson.devDependencies,
      };
      if (deps[toolName]) {
        return true;
      }
    }
    // Try npx
    execSync(`npx ${toolName} --version`, { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

/**
 * Run a linting tool in check mode.
 *
 * @param {string} toolName - Name of the tool to run
 * @param {string[]} args - Arguments to pass to the tool
 * @param {string} cwd - Working directory
 * @returns {boolean} True if check passed, False otherwise
 */
function runToolCheck(toolName, args, cwd) {
  try {
    let cmd;
    // Use npx for local tools
    if (checkNpmTool(toolName)) {
      cmd = `npx ${toolName} ${args.join(' ')}`;
    } else {
      cmd = `${toolName} ${args.join(' ')}`;
    }

    execSync(cmd, {
      cwd,
      stdio: 'inherit',
    });
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * Run a linting tool in fix mode.
 *
 * @param {string} toolName - Name of the tool to run
 * @param {string[]} args - Arguments to pass to the tool
 * @param {string} cwd - Working directory
 * @returns {boolean} True if fix succeeded, False otherwise
 */
function runToolFix(toolName, args, cwd) {
  try {
    let cmd;
    // Use npx for local tools
    if (checkNpmTool(toolName)) {
      cmd = `npx ${toolName} ${args.join(' ')}`;
    } else {
      cmd = `${toolName} ${args.join(' ')}`;
    }

    execSync(cmd, {
      cwd,
      stdio: 'inherit',
    });
    return true;
  } catch (error) {
    return false;
  }
}

// ///////////////////////////////////////////////////////////////
// MAIN LINTING FUNCTIONS
// ///////////////////////////////////////////////////////////////

/**
 * Main linting script function.
 *
 * @param {string} targetPath - Optional path to target directory (default: current directory)
 * @returns {number} Exit code (0 for success, 1 for failure)
 */
function main(targetPath = null) {
  console.log('🚀 React TypeScript linting script started!');
  const targetDir = targetPath ? path.resolve(targetPath) : process.cwd();

  console.log('⚛️  React (TypeScript) Project - Linting Script');
  console.log('='.repeat(50));
  console.log(`📂 Target directory: ${targetDir}`);

  // Check for package.json
  const packageJsonPath = path.join(targetDir, 'package.json');
  if (!fs.existsSync(packageJsonPath)) {
    console.log('❌ No package.json found. This may not be a React TypeScript project.');
    return 1;
  }

  // Check for tsconfig.json
  const tsconfigPath = path.join(targetDir, 'tsconfig.json');
  if (!fs.existsSync(tsconfigPath)) {
    console.log('⚠️  No tsconfig.json found. Type checking may not work correctly.');
  }

  // Check that tools are available
  const tools = ['eslint', 'prettier', 'typescript'];
  const missingTools = [];

  for (const tool of tools) {
    if (!checkNpmTool(tool)) {
      missingTools.push(tool);
    }
  }

  if (missingTools.length > 0) {
    console.log(`❌ Missing tools: ${missingTools.join(', ')}`);
    console.log('Install them with: npm install --save-dev eslint prettier typescript');
    return 1;
  }

  // Automatically detect directories to analyze
  const targetDirs = detectProjectDirs(targetDir);
  if (targetDirs.length === 0) {
    console.log('❌ No TypeScript/TSX folders found');
    return 1;
  }

  console.log(`📁 Analyzing folders: ${targetDirs.join(', ')}`);

  let success = true;

  // 1. Check types with TypeScript
  console.log('🔍 Checking types with TypeScript...');
  const tscSuccess = runToolCheck('tsc', ['--noEmit'], targetDir);
  success = success && tscSuccess;

  // 2. Check linting with ESLint (React + TypeScript rules)
  console.log('🔍 Checking code with ESLint (React + TypeScript)...');
  const eslintArgs = targetDirs.length > 0 ? targetDirs : ['.'];
  const eslintSuccess = runToolCheck('eslint', eslintArgs, targetDir);
  success = success && eslintSuccess;

  // 3. Check formatting with Prettier (JSX support)
  console.log('🔍 Checking formatting with Prettier...');
  const prettierArgs = ['--check', ...targetDirs];
  const prettierSuccess = runToolCheck('prettier', prettierArgs, targetDir);
  success = success && prettierSuccess;

  // Summary
  console.log('\n' + '='.repeat(50));
  if (success) {
    console.log('🎉 All checks passed!');
    console.log('✅ Code meets quality standards.');
    return 0;
  } else {
    console.log('⚠️  Some checks failed.');
    console.log('💡 Use the following commands to fix:');
    console.log(`   cd ${targetDir}`);
    console.log(`   npx prettier --write ${targetDirs.join(' ')}`);
    console.log(`   npx eslint --fix ${targetDirs.join(' ')}`);
    return 1;
  }
}

/**
 * Automatically fix code.
 *
 * @param {string} targetPath - Optional path to target directory (default: current directory)
 * @returns {number} Exit code (0 for success, 1 for failure)
 */
function fixCode(targetPath = null) {
  const targetDir = targetPath ? path.resolve(targetPath) : process.cwd();

  console.log('🔧 React (TypeScript) Project - Automatic code fixing');
  console.log('='.repeat(50));
  console.log(`📂 Target directory: ${targetDir}`);

  // Detect directories
  const targetDirs = detectProjectDirs(targetDir);
  if (targetDirs.length === 0) {
    console.log('❌ No TypeScript/TSX folders found');
    return 1;
  }

  console.log(`📁 Formatting folders: ${targetDirs.join(', ')}`);

  let success = true;

  // 1. Format with Prettier
  console.log('🎨 Formatting with Prettier...');
  const prettierSuccess = runToolFix('prettier', ['--write', ...targetDirs], targetDir);
  success = success && prettierSuccess;

  // 2. Fix with ESLint
  console.log('🔧 Fixing issues with ESLint...');
  const eslintArgs = ['--fix', ...targetDirs];
  const eslintSuccess = runToolFix('eslint', eslintArgs, targetDir);
  success = success && eslintSuccess;

  // Note: TypeScript type errors cannot be auto-fixed
  console.log('ℹ️  Note: TypeScript type errors must be fixed manually.');

  // Summary
  console.log('\n' + '='.repeat(50));
  if (success) {
    console.log('🎉 Automatic fixes completed!');
    console.log('✅ Code has been formatted and organized.');
    return 0;
  } else {
    console.log('⚠️  Some fixes failed.');
    return 1;
  }
}

// ///////////////////////////////////////////////////////////////
// ENTRY POINT
// ///////////////////////////////////////////////////////////////

// Check command line arguments
const args = process.argv.slice(2);
const targetPath = args[0] || null;
const shouldFix = args.includes('--fix') || args.includes('-f');

if (shouldFix) {
  process.exit(fixCode(targetPath));
} else {
  process.exit(main(targetPath));
}


