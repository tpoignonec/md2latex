%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% ICube IRIS QMS-like LaTeX Class
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%----------------------------------------------------------------------------------------
%	BASE CLASS CONFIGURATION
%----------------------------------------------------------------------------------------

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{iris-qms}[2025/10/30 iris-qms Class v1.0]


\DeclareOption*{\PassOptionsToClass{\CurrentOption}{iris-report}}
\ProcessOptions\relax % Process class options

\LoadClass{iris-report} % Load the base class

%----------------------------------------------------------------------------------------
%	Front page customization for QMS documents
%----------------------------------------------------------------------------------------

/