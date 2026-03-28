
				const registerAllyAction = () => {
					if ( ! window?.elementorAppConfig?.hasPro || ! window?.elementorFrontend?.utils?.urlActions ) {
						return;
					}

					elementorFrontend.utils.urlActions.addAction( 'allyWidget:open', () => {
						if ( window?.ea11yWidget?.widget?.open ) {
							window.ea11yWidget.widget.open();
						}
					} );
				};

				const waitingLimit = 30;
				let retryCounter = 0;

				const waitForElementorPro = () => {
					return new Promise( ( resolve ) => {
						const intervalId = setInterval( () => {
							if ( retryCounter === waitingLimit ) {
								resolve( null );
							}

							retryCounter++;

							if ( window.elementorFrontend && window?.elementorFrontend?.utils?.urlActions ) {
								clearInterval( intervalId );
								resolve( window.elementorFrontend );
							}
								}, 100 ); // Check every 100 milliseconds for availability of elementorFrontend
					});
				};

				waitForElementorPro().then( () => { registerAllyAction(); });
			