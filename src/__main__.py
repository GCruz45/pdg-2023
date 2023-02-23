import sys
import os

from src.USGSDownloader import USGSDownloader


def display_title_bar():
    # Clears the terminal screen, and displays a title bar.
    os.system('cls')

    print("\t**********************************************")
    print("\t*  DLInpainter - Satellite Image Inpainting  *")
    print("\t**********************************************")


def main_menu_choice():
    display_title_bar()

    print("\n[1] Set image provider.")
    print("[2] Select inpainting method.")
    print("[3] Execute inpainting.")
    print("[4] View current parameters.")
    print("[q] Quit.")

    return input("What would you like to do? \n")


def image_provider_choice():
    print("\n[1] USGS/EROS.")
    print("[q] Back.")

    choice = ''
    while choice != 'q':
        choice = input("What would you like to do? \n")
        if choice == '1':
            global img_provider
            img_provider = USGSDownloader()
            image_parameter_choice()
        elif choice == '2':
            print("\nNo other provider available at the moment.\n")
        elif choice == 'q':
            return
        else:
            print("\nI didn't understand that choice.\n")


def image_parameter_choice():
    print("\n[1] Dataset name       (Default = \"gls_all\").")
    print("[2] Number of results    (Default = 10).")
    print("[3] Filters (May include coordinates).")
    print("[4] View currently configured parameters.")
    print("[5] Erase all currently configured parameters.")
    print("[6] Execute scene search.")
    print("[q] Back.")

    choice = ''
    while choice != 'q':
        choice = input("What would you like to do? \n")
        if choice == '1':
            img_provider.datasetName = input("Enter dataset name:\n")
        elif choice == '2':
            img_provider.maxResults = input("Enter the desired number of results:\n")
        elif choice == '3':
            filter_creation_choice()
        elif choice == '4': # TODO HERE
            return
        elif choice == '5': # TODO
            return
        elif choice == '6': # TODO
            return
        elif choice == 'q':
            return
            return
        else:
            print("\nI didn't understand that choice.\n")


def filter_creation_choice():
    print("\n[1] Create a spatial filter (mbr).")
    print("[2] Create a spatial filter (GeoJson).")
    print("[3] Create a cloud cover filter.")
    print("[q] Back.")

    choice = ''
    while choice != 'q':
        choice = input("What would you like to do? \n")
        if choice == '1': # TODO HERE
            return
        elif choice == '2': # TODO
            return
        elif choice == '3': # TODO
            return
        elif choice == 'q':
            return
        else:
            print("\nI didn't understand that choice.\n")


def create_spatial_filter_mbr():
    ll_corner = input("Indicate the lower left corner (lat, long), space separated \n")
    ll_corner = ll_corner.split(" ")
    ll_corner_lat = ll_corner[0]
    ll_corner_long = ll_corner[1]

    filter = ""

def inpainting_method_choice(): # TODO while loop
    print("\n[1] ML inpainting.")
    print("[2] Basic inpainting.")
    print("[q] Back.")

    return input("What would you like to do? \n")


def basic_inpainting_choice(): # TODO while loop
    print("\n[1] Navier Stokes.")
    print("[2] Telea.")
    print("[3] Biharmonic.")
    print("[q] Back.")

    return input("What would you like to do? \n")


def ml_inpainting_choice(): # TODO while loop
    print("\n[1] ???.")
    print("[q] Back.")

    return input("What would you like to do? \n")


def main_menu():
    # Set up a loop where users can choose what they'd like to do.

    display_title_bar()
    print("\n[1] Set image provider.")
    print("[2] Select inpainting method.")
    print("[3] Execute inpainting.")
    print("[4] View current parameters.")
    print("[q] Quit.")

    choice = ''
    while choice != 'q':

        choice = input("What would you like to do? \n")

        # Respond to the user's choice.
        if choice == '1':  # Set img provider
            image_provider_choice()
        elif choice == '2': # TODO
            print("\n???\n")
        elif choice == '3': # TODO
            print("\n???\n")
        elif choice == '4': # TODO
            print("\n???\n")
        elif choice == 'q':
            print("\nThanks. Bye.")
        else:
            print("\nI didn't understand that choice.\n")


datasetName = "gls_all"
maxResults = 100
sceneFilter = None


def create_scene_search_json():
    return


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    # MAIN PROGRAM #
    main_menu()

    return 1
    # Do argument parsing here (eg. with argparse) and anything else
    # you want your project to do. Return values are exit codes.


img_provider = None

if __name__ == "__main__":
    sys.exit(main())
