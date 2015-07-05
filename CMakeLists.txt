cmake_minimum_required(VERSION 2.8.7)

project(WorkflowOrganizer)

set(EXTENSION_NAME WorkflowOrganizer)
set(EXTENSION_HOMEPAGE "http://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Modules/WorkflowOrganizer")
set(EXTENSION_CATEGORY "IGT")
set(EXTENSION_CONTRIBUTORS "Junichi Tokuda (BWH) and Atsushi Yamada (Shiga University of Medical Science in Japan)")
set(EXTENSION_DESCRIPTION "This module only binds the existing modules that are required for given clinical applications, and allows the users to go through those modules by simply clicking the navigation buttons.")
set(EXTENSION_ICONURL "http://www.slicer.org/slicerWiki/images/4/4c/WoLogo.png")
set(EXTENSION_SCREENSHOTURLS "http://www.slicer.org/slicerWiki/images/1/1f/IgtWizardGUISample3.png")

find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

add_subdirectory(WorkflowOrganizer)

include(${Slicer_EXTENSION_CPACK})
